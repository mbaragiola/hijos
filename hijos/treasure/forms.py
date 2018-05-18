from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mass_mail
from django.forms import Form
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from hijos.users.models import Affiliation, Lodge


class SendAccountBalanceForm(Form):

    def send_email(self, affiliation):
        title = _("Your current account balance on %(lodge)s") % {
            'lodge': str(affiliation.lodge)
        }
        affiliation.send_treasure_mail(title)

    def send_mass_email(self, lodge):
        title = _("Your current account balance on %(lodge)s") % {
            'lodge': str(lodge)
        }

        data_tuple = []
        for affiliation in lodge.affiliations.filter(is_active=True).all():
            if affiliation.user.most_worshipful:
                body = _("Dear M.·.W.·.B.·. %(full_name)s:")
            elif affiliation.user.worshipful:
                body = _("Dear W.·.B.·. %(full_name)s:")
            elif affiliation.user.past_master:
                body = _("Dear P.·.M.·. %(full_name)s:")
            else:
                body = _("Dear B.·. %(full_name)s:")

            body = body % {'full_name': affiliation.user.get_full_name()}
            body += "\n\n\t"
            body += _(
                "Your current account balance with %(lodge)s is of $ %(balance)s"
            ) % {
                'lodge': str(lodge),
                'balance': str(affiliation.account.balance)
            }
            data_tuple.append(
                (
                    title,
                    body % {
                    },
                    lodge.treasurer.email,
                    [affiliation.user.email]
                )
            )

        send_mass_mail(data_tuple)


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


class SendMassAccountBalance(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = Lodge
    template_name = 'users/lodge_detail.html'
    form_class = SendAccountBalanceForm

    def form_valid(self, form):
        form.send_mass_email(self.object)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'users:lodge-detail', kwargs={'pk': self.object.pk}
        )
