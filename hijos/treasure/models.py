from decimal import Decimal

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from hijos.users import models as users


class LodgeAccount(users.Model):
    """
    """
    lodge = models.ForeignKey(
        users.Lodge,
        verbose_name=_('lodge'),
        related_name='lodge_accounts',
        related_query_name='lodge_account',
        on_delete=models.PROTECT,
        db_index=True
    )
    code = models.CharField(
        _('code'),
        max_length=10
    )
    name = models.CharField(
        _('name'),
        max_length=150
    )
    description = models.CharField(
        _('description'),
        max_length=500,
        default="",
        blank=True
    )
    balance = models.DecimalField(
        _('balance'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True
    )

    def __str__(self):
        return str(self.code) + ' - ' + str(self.name)

    class Meta:
        verbose_name = _('lodge account')
        verbose_name_plural = _('lodge accounts')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['code']


class Account(users.Model):
    """
    """
    affiliation = models.OneToOneField(
        users.Affiliation,
        verbose_name=_('affiliation'),
        related_name='account',
        on_delete=models.PROTECT,
        db_index=True
    )
    balance = models.DecimalField(
        _('balance'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True
    )

    def __str__(self):
        return str(self.affiliation) + ' - $ ' + str(self.balance)

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['affiliation']


LODGEACCOUNTMOVEMENT_INGRESS = 'I'
LODGEACCOUNTMOVEMENT_EGRESS = 'E'
LODGEACCOUNTMOVEMENT_DEPOSIT = 'D'
LODGEACCOUNT_MOVEMENT_TYPES = (
    (LODGEACCOUNTMOVEMENT_INGRESS, _('Ingress')),
    (LODGEACCOUNTMOVEMENT_EGRESS, _('Egress')),
    (LODGEACCOUNTMOVEMENT_DEPOSIT, _('Deposit'))
)


class LodgeAccountMovement(users.Model):
    """
    """
    lodge_account = models.ForeignKey(
        LodgeAccount,
        verbose_name=_('lodge account'),
        related_name='movements',
        related_query_name='movement',
        on_delete=models.PROTECT,
        db_index=True
    )
    description = models.CharField(
        _('description'),
        max_length=150
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2
    )
    lodgeaccount_movement_type = models.CharField(
        _('lodge account movement type'),
        max_length=1,
        choices=LODGEACCOUNT_MOVEMENT_TYPES
    )
    object_ct = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT
    )
    object_id = models.BigIntegerField()
    content_object = GenericForeignKey(
        'object_ct',
        'object_id'
    )

    def __str__(self):
        return str(self.amount)

    class Meta:
        verbose_name = _('lodge account movement')
        verbose_name_plural = _('lodge account movements')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']


ACCOUNTMOVEMENT_INVOICE = 'I'
ACCOUNTMOVEMENT_DEPOSIT = 'D'
ACCOUNTMOVEMENT_CHARGE = 'C'
ACCOUNT_MOVEMENT_TYPES = (
    (ACCOUNTMOVEMENT_INVOICE, _('Invoice')),
    (ACCOUNTMOVEMENT_DEPOSIT, _('Deposit')),
    (ACCOUNTMOVEMENT_CHARGE, _('Charge'))
)


class AccountMovement(users.Model):
    """
    """
    account = models.ForeignKey(
        Account,
        verbose_name=_('account'),
        related_name='movements',
        related_query_name='movement',
        on_delete=models.PROTECT,
        db_index=True
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2
    )
    account_movement_type = models.CharField(
        _('account movement type'),
        max_length=1,
        choices=ACCOUNT_MOVEMENT_TYPES
    )
    object_ct = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT
    )
    object_id = models.BigIntegerField()
    content_object = GenericForeignKey(
        'object_ct',
        'object_id'
    )

    def __str__(self):
        return str(self.amount)

    class Meta:
        verbose_name = _('account movement')
        verbose_name_plural = _('account movements')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']


class Period(users.Model):
    """
    A period can be a month, a quarter, a whole year, etc.
    """
    lodge = models.ForeignKey(
        users.Lodge,
        verbose_name=_('lodge'),
        related_name='periods',
        related_query_name='period',
        on_delete=models.PROTECT,
        db_index=True
    )
    begin = models.DateField(
        _('begin')
    )
    end = models.DateField(
        _('end')
    )
    simple_affiliation_price = models.DecimalField(
        _('simple affiliation price'),
        max_digits=12,
        decimal_places=2,
        help_text=_("Usually GL price plus an extra.")
    )
    multiple_affiliation_price = models.DecimalField(
        _('multiple affiliation price'),
        max_digits=12,
        decimal_places=2,
        help_text=_("Usually just the GL price.")
    )

    def __str__(self):
        return str(self.begin) + '-' + str(self.end)

    class Meta:
        verbose_name = _('period')
        verbose_name_plural = _('periods')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-begin']


class Invoice(users.Model):
    """
    """
    period = models.ForeignKey(
        Period,
        verbose_name=_('period'),
        related_name='invoices',
        related_query_name='invoice',
        on_delete=models.PROTECT,
        db_index=True
    )
    affiliation = models.ForeignKey(
        users.Affiliation,
        verbose_name=_('affiliation'),
        related_name='invoices',
        related_query_name='invoice',
        on_delete=models.PROTECT,
        db_index=True
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator('0.01')]
    )
    account_movement = GenericRelation(
        AccountMovement,
        related_query_name='treasure_account_invoice',
        content_type_field='object_ct',
        object_id_field='object_id'
    )

    def __str__(self):
        return str(self.period) + ': $ ' + str(self.amount)

    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']


class Deposit(users.Model):
    """
    """
    affiliation = models.ForeignKey(
        users.Affiliation,
        verbose_name=_('affiliation'),
        related_name='deposits',
        related_query_name='deposit',
        on_delete=models.PROTECT,
        db_index=True
    )
    to_grand_lodge = models.BooleanField(
        _('to grand lodge'),
        default=False,
        blank=True
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator('0.01')]
    )
    description = models.CharField(
        _('description'),
        max_length=300,
        default="",
        blank=True,
        help_text=_("Optional description.")
    )
    receipt = models.FileField(
        _('receipt'),
        upload_to='receipts',
        blank=True,
        null=True
    )
    account_movement = GenericRelation(
        AccountMovement,
        related_query_name='treasure_account_deposit',
        content_type_field='object_ct',
        object_id_field='object_id'
    )
    lodge_account_movement = GenericRelation(
        LodgeAccountMovement,
        related_query_name='treasure_lodgeaccount_deposit',
        content_type_field='object_ct',
        object_id_field='object_id'
    )

    class Meta:
        verbose_name = _('deposit')
        verbose_name_plural = _('deposits')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']


CHARGE_INITIATION = 'I'
CHARGE_PASS = 'P'
CHARGE_RAISE = 'R'
CHARGE_OTHER = 'O'
CHARGE_TYPES = (
    (CHARGE_INITIATION, _('Initiation')),
    (CHARGE_PASS, _('Pass')),
    (CHARGE_RAISE, _('Raise')),
    (CHARGE_OTHER, _('Other'))
)


class Charge(users.Model):
    """
    """
    affiliation = models.ForeignKey(
        users.Affiliation,
        verbose_name=_('affiliation'),
        related_name='charges',
        related_query_name='charge',
        on_delete=models.PROTECT,
        db_index=True
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator('0.01')]
    )
    charge_type = models.CharField(
        _('charge type'),
        max_length=1,
        choices=CHARGE_TYPES
    )
    description = models.CharField(
        _('description'),
        max_length=300,
        default="",
        blank=True,
        help_text=_("Optional description.")
    )
    account_movement = GenericRelation(
        AccountMovement,
        related_query_name='treasure_account_charge',
        content_type_field='object_ct',
        object_id_field='object_id'
    )

    class Meta:
        verbose_name = _('charge')
        verbose_name_plural = _('charges')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']


EGRESS_TYPE_DONATION = 'D'
EGRESS_TYPE_PHILANTROPY = 'PH'
EGRESS_TYPE_EXPENSES = 'E'
EGRESS_TYPE_LOAN = 'L'
EGRESS_TYPE_GRANDLODGE_TRANSFER = 'GLT'
EGRESS_TYPE_OTHER = 'O'
EGRESS_TYPES = (
    (EGRESS_TYPE_DONATION, _('Donation')),
    (EGRESS_TYPE_PHILANTROPY, _('Philantropy')),
    (EGRESS_TYPE_EXPENSES, _('Expenses')),
    (EGRESS_TYPE_LOAN, _('Loan')),
    (EGRESS_TYPE_GRANDLODGE_TRANSFER, _('Grand Lodge Transfer')),
    (EGRESS_TYPE_OTHER, _('Other'))
)


class LodgeAccountEgress(users.Model):
    """
    """
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator('0.01')]
    )
    egress_type = models.CharField(
        _('egress type'),
        max_length=3,
        choices=EGRESS_TYPES
    )
    description = models.CharField(
        _('description'),
        max_length=300,
        default="",
        blank=True,
        help_text=_("Optional description.")
    )
    receipt = models.FileField(
        _('receipt'),
        upload_to='receipts',
        blank=True,
        null=True
    )
    lodge_account_movement = GenericRelation(
        LodgeAccountMovement,
        related_query_name='treasure_lodgeaccount_egress',
        content_type_field='object_ct',
        object_id_field='object_id'
    )

    class Meta:
        verbose_name = _('lodge account egress')
        verbose_name_plural = _('lodge account egresses')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']


INGRESS_TYPE_DONATION = 'D'
INGRESS_TYPE_PHILANTROPY = 'PH'
INGRESS_TYPE_PAYMENT = 'PA'
INGRESS_TYPE_OTHER = 'O'
INGRESS_TYPES = (
    (INGRESS_TYPE_DONATION, _('Donation')),
    (INGRESS_TYPE_PHILANTROPY, _('Philantropy')),
    (INGRESS_TYPE_PAYMENT, _('Payment')),
    (INGRESS_TYPE_OTHER, _('Other'))
)


class LodgeAccountIngress(users.Model):
    """
    """
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator('0.01')]
    )
    ingress_type = models.CharField(
        _('ingress type'),
        max_length=3,
        choices=INGRESS_TYPES
    )
    description = models.CharField(
        _('description'),
        max_length=300,
        default="",
        blank=True,
        help_text=_("Optional description.")
    )
    receipt = models.FileField(
        _('receipt'),
        upload_to='receipts',
        blank=True,
        null=True
    )
    lodge_account_movement = GenericRelation(
        LodgeAccountMovement,
        related_query_name='treasure_lodgeaccount_ingress',
        content_type_field='object_ct',
        object_id_field='object_id'
    )

    class Meta:
        verbose_name = _('lodge account ingress')
        verbose_name_plural = _('lodge account ingresses')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']
