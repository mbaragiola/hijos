from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from hijos.users.models import Affiliation


class SendAccountBalanceForm(Form):

    def send_email(self, affiliation):
        title = _("Your current account balance on %(lodge)s") % {
            'lodge': str(affiliation.lodge)
        }
        affiliation.send_treasure_mail(title)


class SendAccountBalance(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = Affiliation
    template_name = 'users/affiliation_detail.html'
    form_class = SendAccountBalanceForm

    def form_valid(self, form):
        form.send_email(self.object)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'users:affiliation-detail', kwargs={'pk': self.object.pk}
        )
