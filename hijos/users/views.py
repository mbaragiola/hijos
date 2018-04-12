from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView

from hijos.treasure import models as treasure
from hijos.users import models


class UserDetailView(LoginRequiredMixin, DetailView):
    model = models.User
    object_name = 'user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            account = treasure.Account.objects.get(user=self.user)
        except treasure.Account.DoesNotExist:
            context['account'] = None
        else:
            context['account'] = account


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserListView(LoginRequiredMixin, ListView):
    model = models.User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'
