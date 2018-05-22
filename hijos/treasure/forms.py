from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mass_mail
from django.forms import Form
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from hijos.treasure import models
from hijos.users.models import Affiliation, Lodge


class SendAccountBalanceForm(Form):

    def send_email(self, affiliation):
        title = _("Your current account balance on %(lodge)s") % {
            'lodge': str(affiliation.lodge)
        }
        affiliation.account.send_treasure_mail(title)

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

            last_movements = (_(
                "\n\nYour last 10 movements are:"
                "\n\nDate\tType\t\tAmount\t\tBalance\n\n"
            ))
            account_movements = (
                affiliation.account.movements.filter(is_active=True)[:10]
            )
            for m in account_movements.all():
                if m.account_movement_type == models.ACCOUNTMOVEMENT_INVOICE:
                    movement_type = _('Invoice')
                elif m.account_movement_type == models.ACCOUNTMOVEMENT_DEPOSIT:
                    movement_type = _('Deposit')
                elif m.account_movement_type == (
                    models.ACCOUNTMOVEMENT_GRANDLODGEDEPOSIT
                ):
                    movement_type = _('Grand Lodge Deposit')
                elif m.account_movement_type == models.ACCOUNTMOVEMENT_CHARGE:
                    movement_type = _('Charge')
                else:
                    movement_type = _('Unknown')

                last_movements += (
                    "%(date)s\t%(type)s\t\t%(amount)s\t\t%(balance)s\n"
                ) % {
                    'date': str(m.created_on.date()),
                    'type': movement_type,
                    'amount': str(m.amount),
                    'balance': str(m.balance)
                }

            data_tuple.append(
                (
                    title,
                    body + last_movements,
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
