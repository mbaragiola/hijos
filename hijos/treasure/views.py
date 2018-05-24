from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Max, Min, Q, Sum
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, ListView

from hijos.treasure import models
from hijos.users import models as users


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


class LodgeAccountCreateView(LoginRequiredMixin, CreateView):
    model = models.LodgeAccount
    fields = ['handler', 'description']
    template_name = 'treasure/lodgeaccount_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)


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


class PeriodCreateView(LoginRequiredMixin, CreateView):
    model = models.Period
    fields = ['lodge', 'begin', 'end', 'price_multiplier', 'send_email']
    template_name = 'treasure/period_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)


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


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = models.Invoice
    fields = ['period', 'affiliation', 'amount', 'send_email']
    template_name = 'treasure/invoice_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)


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


class DepositCreateView(LoginRequiredMixin, CreateView):
    model = models.Deposit
    fields = [
        'payer',
        'lodge_account',
        'amount',
        'description',
        'send_email',
        'receipt'
    ]
    template_name = 'treasure/deposit_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)


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


class ChargeCreateView(LoginRequiredMixin, CreateView):
    model = models.Charge
    fields = [
        'debtor',
        'charge_type',
        'amount',
        'description',
        'send_email'
    ]
    template_name = 'treasure/charge_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)


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


class GrandLodgeDepositCreateView(LoginRequiredMixin, CreateView):
    model = models.GrandLodgeDeposit
    fields = [
        'payer',
        'status',
        'amount',
        'description',
        'receipt',
        'send_email'
    ]
    template_name = 'treasure/grandlodgedeposit_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)


class LodgeAccountIngressesByLodgeList(LoginRequiredMixin, ListView):
    template_name = 'treasure/lodgeaccountingresses_list.html'
    context_object_name = 'ingresses'

    def get_queryset(self):
        self.lodge = get_object_or_404(
            users.Lodge, pk=self.kwargs['pk']
        )
        return models.LodgeAccountIngress.objects.filter(
            lodge_account__handler__lodge=self.lodge
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lodge'] = self.lodge
        return context


class LodgeAccountIngressDetailView(LoginRequiredMixin, DetailView):
    model = models.LodgeAccountIngress
    context_object_name = 'ingress'
    template_name = 'treasure/lodgeaccountingress_detail.html'


class LodgeAccountIngressCreateView(LoginRequiredMixin, CreateView):
    model = models.LodgeAccountIngress
    fields = [
        'lodge_account',
        'ingress_type',
        'amount',
        'description',
        'receipt'
    ]
    template_name = 'treasure/lodgeaccountingress_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)


class LodgeAccountEgressesByLodgeList(LoginRequiredMixin, ListView):
    template_name = 'treasure/lodgeaccountegresses_list.html'
    context_object_name = 'egresses'

    def get_queryset(self):
        self.lodge = get_object_or_404(
            users.Lodge, pk=self.kwargs['pk']
        )
        return models.LodgeAccountEgress.objects.filter(
            lodge_account__handler__lodge=self.lodge
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lodge'] = self.lodge
        return context


class LodgeAccountEgressDetailView(LoginRequiredMixin, DetailView):
    model = models.LodgeAccountEgress
    context_object_name = 'egress'
    template_name = 'treasure/lodgeaccountegress_detail.html'


class LodgeAccountEgressCreateView(LoginRequiredMixin, CreateView):
    model = models.LodgeAccountEgress
    fields = [
        'lodge_account',
        'egress_type',
        'amount',
        'description',
        'receipt'
    ]
    template_name = 'treasure/lodgeaccountegress_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)


class LodgeAccountTransfersByLodgeList(LoginRequiredMixin, ListView):
    template_name = 'treasure/lodgeaccounttransfer_list.html'
    context_object_name = 'transfers'

    def get_queryset(self):
        self.lodge = get_object_or_404(
            users.Lodge, pk=self.kwargs['pk']
        )
        return models.LodgeAccountTransfer.objects.filter(
            Q(lodge_account_from__handler__lodge=self.lodge) |
            Q(lodge_account_to__handler__lodge=self.lodge)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lodge'] = self.lodge
        return context


class LodgeAccountTransferDetailView(LoginRequiredMixin, DetailView):
    model = models.LodgeAccountTransfer
    context_object_name = 'transfer'
    template_name = 'treasure/lodgeaccounttransfer_detail.html'


class LodgeAccountTransferCreateView(LoginRequiredMixin, CreateView):
    model = models.LodgeAccountTransfer
    fields = [
        'lodge_account_from',
        'lodge_account_to',
        'amount',
        'description'
    ]
    template_name = 'treasure/lodgeaccounttransfer_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)


class DebtorsByLodgeList(LoginRequiredMixin, ListView):
    template_name = 'treasure/debtors_list.html'
    context_object_name = 'debtor_accounts'

    def get_queryset(self):
        self.lodge = get_object_or_404(
            users.Lodge, pk=self.kwargs['pk']
        )
        return models.Account.objects.filter(
            affiliation__lodge=self.lodge,
            balance__lt=Decimal('0.00')
        ).order_by('balance')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lodge'] = self.lodge
        context['aggregations'] = self.object_list.aggregate(
            debt_sum=Sum('balance'),
            debt_avg=Avg('balance'),
            debt_max=Max('balance'),
            debt_min=Min('balance')
        )
        return context
