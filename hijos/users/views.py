from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import DetailView, ListView

from hijos.treasure.forms import SendAccountBalance, SendAccountBalanceForm
from hijos.users import models


class UserDetailView(LoginRequiredMixin, DetailView):
    model = models.User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'
    slug_field = 'username'
    slug_url_kwarg = 'username'


class LodgesList(LoginRequiredMixin, ListView):
    template_name = 'users/lodge_list.html'
    context_object_name = 'lodges'

    def get_queryset(self):
        return models.Lodge.objects.filter(is_active=True)


class LodgeDetailView(LoginRequiredMixin, DetailView):
    model = models.Lodge
    template_name = 'users/lodge_detail.html'
    context_object_name = 'lodge'


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
        context['form'] = SendAccountBalanceForm()
        return context


class AffiliationDetailView(View):

    def get(self, request, *args, **kwargs):
        view = AffiliationDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = SendAccountBalance.as_view()
        return view(request, *args, **kwargs)


class UserListView(LoginRequiredMixin, ListView):
    model = models.User
    slug_field = 'username'
    slug_url_kwarg = 'username'
