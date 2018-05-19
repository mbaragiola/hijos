from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from hijos.treasure import forms
from hijos.users import models


class UserDetailView(LoginRequiredMixin, DetailView):
    model = models.User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserCreateView(LoginRequiredMixin, CreateView):
    model = models.User
    fields = [
        'username',
        'first_name',
        'last_name',
        'email',
        'degree',
        'initiated',
        'passed',
        'raised',
        'past_master',
        'worshipful',
        'most_worshipful'
    ]
    template_name = 'users/user_add.html'

    def form_valid(self, form):
        form.instance.is_active = False
        form.instance.password = models.User.objects.make_random_password()
        return super().form_valid(form)


class UserListView(LoginRequiredMixin, ListView):
    model = models.User
    slug_field = 'username'
    slug_url_kwarg = 'username'


class LodgesList(LoginRequiredMixin, ListView):
    template_name = 'users/lodge_list.html'
    context_object_name = 'lodges'

    def get_queryset(self):
        return models.Lodge.objects.filter(is_active=True)


class LodgeDisplayView(LoginRequiredMixin, DetailView):
    model = models.Lodge
    template_name = 'users/lodge_detail.html'
    context_object_name = 'lodge'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.SendAccountBalanceForm()
        return context


class LodgeDetailView(View):

    def get(self, request, *args, **kwargs):
        view = LodgeDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = forms.SendMassAccountBalance.as_view()
        return view(request, *args, **kwargs)


class AffiliationsByLodgeList(LoginRequiredMixin, ListView):
    template_name = 'users/affiliation_list.html'
    context_object_name = 'affiliations'

    def get_queryset(self):
        self.lodge = get_object_or_404(
            models.Lodge, pk=self.kwargs['pk']
        )
        return models.Affiliation.objects.filter(lodge=self.lodge)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lodge'] = self.lodge
        return context


class AffiliationDisplayView(LoginRequiredMixin, DetailView):
    model = models.Affiliation
    template_name = 'users/affiliation_detail.html'
    context_object_name = 'affiliation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.SendAccountBalanceForm()
        return context


class AffiliationDetailView(View):

    def get(self, request, *args, **kwargs):
        view = AffiliationDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = forms.SendAccountBalance.as_view()
        return view(request, *args, **kwargs)


class AffiliationCreateView(LoginRequiredMixin, CreateView):
    model = models.Affiliation
    fields = ['lodge', 'user', 'category']
    template_name = 'users/affiliation_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)
