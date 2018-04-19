from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404

from hijos.users import models as users
from hijos.treasure import models


class LodgeAccountsByLodgeList(LoginRequiredMixin, ListView):
    template_name = 'treasure/lodgeaccount_list.html'
    context_object_name = 'lodge_accounts'

    def get_queryset(self):
        self.lodge = get_object_or_404(
            users.Lodge, pk=self.kwargs['pk']
        )
        return models.LodgeAccount.objects.filter(
            handler__lodge=self.lodge
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lodge'] = self.lodge
        return context


class LodgeAccountDetailView(LoginRequiredMixin, DetailView):
    model = models.LodgeAccount
    context_object_name = 'lodge_account'
    template_name = 'treasure/lodgeaccount_detail.html'


class PeriodsByLodgeList(LoginRequiredMixin, ListView):
    template_name = 'treasure/period_list.html'
    context_object_name = 'periods'

    def get_queryset(self):
        self.lodge = get_object_or_404(
            users.Lodge, pk=self.kwargs['pk']
        )
        return models.Period.objects.filter(
            lodge=self.lodge
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lodge'] = self.lodge
        return context


class PeriodDetailView(LoginRequiredMixin, DetailView):
    model = models.Period
    context_object_name = 'period'
    template_name = 'treasure/period_detail.html'


class InvoicesByLodgeList(LoginRequiredMixin, ListView):
    template_name = 'treasure/invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        self.lodge = get_object_or_404(
            users.Lodge, pk=self.kwargs['pk']
        )
        return models.Invoice.objects.filter(
            period__lodge=self.lodge
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lodge'] = self.lodge
        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = models.Invoice
    context_object_name = 'invoice'
    template_name = 'treasure/invoice_detail.html'


class DepositsByLodgeList(LoginRequiredMixin, ListView):
    template_name = 'treasure/deposit_list.html'
    context_object_name = 'deposits'

    def get_queryset(self):
        self.lodge = get_object_or_404(
            users.Lodge, pk=self.kwargs['pk']
        )
        return models.Deposit.objects.filter(
            payer__lodge=self.lodge
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lodge'] = self.lodge
        return context


class DepositDetailView(LoginRequiredMixin, DetailView):
    model = models.Deposit
    context_object_name = 'deposit'
    template_name = 'treasure/deposit_detail.html'


class ChargesByLodgeList(LoginRequiredMixin, ListView):
    template_name = 'treasure/charge_list.html'
    context_object_name = 'charges'

    def get_queryset(self):
        self.lodge = get_object_or_404(
            users.Lodge, pk=self.kwargs['pk']
        )
        return models.Charge.objects.filter(
            debtor__lodge=self.lodge
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lodge'] = self.lodge
        return context


class ChargeDetailView(LoginRequiredMixin, DetailView):
    model = models.Charge
    context_object_name = 'charge'
    template_name = 'treasure/charge_detail.html'


class GrandLodgeDepositsByLodgeList(LoginRequiredMixin, ListView):
    template_name = 'treasure/grandlodgedeposit_list.html'
    context_object_name = 'grand_lodge_deposits'

    def get_queryset(self):
        self.lodge = get_object_or_404(
            users.Lodge, pk=self.kwargs['pk']
        )
        return models.GrandLodgeDeposit.objects.filter(
            payer__lodge=self.lodge
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lodge'] = self.lodge
        return context


class GrandLodgeDepositDetailView(LoginRequiredMixin, DetailView):
    model = models.GrandLodgeDeposit
    context_object_name = 'grand_lodge_deposit'
    template_name = 'treasure/grandlodgedeposit_detail.html'
