from decimal import Decimal

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from hijos.users import models as users


class LodgeGlobalAccount(users.Model):
    """
    """
    lodge = models.OneToOneField(
        users.Lodge,
        verbose_name=_('lodge'),
        related_name='lodge_global_account',
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
        return str(self.lodge)

    def get_absolute_url(self):
        return reverse(
            'treasure:lodgeglobalaccount-detail', kwargs={'pk': self.pk}
        )

    class Meta:
        verbose_name = _('lodge global account')
        verbose_name_plural = _('lodge global accounts')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['lodge']


class LodgeAccount(users.Model):
    """
    There could be multiple brothers receiving payments, making payments on
    behalf of the lodge, or simply stashing lodge's funds.
    """
    handler = models.ForeignKey(
        users.Affiliation,
        verbose_name=_('handler'),
        related_name='lodge_accounts',
        related_query_name='lodge_account',
        on_delete=models.PROTECT,
        db_index=True
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
        return str(self.handler)

    def get_absolute_url(self):
        return reverse('treasure:lodgeaccount-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('lodge account')
        verbose_name_plural = _('lodge accounts')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['handler']


class Account(users.Model):
    """
    Each user has an account for every lodge he is affiliated with.
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

    def get_absolute_url(self):
        return reverse('treasure:account-detail', kwargs={'pk': self.pk})

    def send_treasure_mail(self, title, content=""):
        if self.affiliation.user.most_worshipful:
            body = _("Dear M.·.W.·.B.·. %(full_name)s:")
        elif self.affiliation.user.worshipful:
            body = _("Dear W.·.B.·. %(full_name)s:")
        elif self.affiliation.user.past_master:
            body = _("Dear P.·.M.·. %(full_name)s:")
        else:
            body = _("Dear B.·. %(full_name)s:")

        body = body % {'full_name': self.affiliation.user.get_full_name()}
        body_html = '<p>' + body + '</p>'
        body += "\n\t" + content + "\n\t"

        if content is not None and content != "":
            body_html += (
                "<p>&nbsp;&nbsp;&nbsp;&nbsp;" + content +
                "</p>&nbsp;&nbsp;&nbsp;&nbsp;"
            )

        account_balance = _(
            "Your current account balance with %(lodge)s is of $ %(balance)s"
        ) % {
            'lodge': str(self.affiliation.lodge),
            'balance': str(self.balance)
        }
        account_balance_html = (
            "<p>&nbsp;&nbsp;&nbsp;&nbsp;" + account_balance + "</p>"
        )

        last_movements = (_(
            "\n\nYour last 10 movements are:"
            "\n\nDate\tType\t\tAmount\t\tBalance\n\n"
        ))
        last_movements_html = (_(
            "<br><br>Your last 10 movements are:"
            "<br><br>"
            "<table>"
            "<thead>"
            "<tr>"
            "<th>Date</th>"
            "<th>Type</th>"
            "<th>Amount</th>"
            "<th>Balance</th>"
            "</tr>"
            "</thead>"
            "<tbody>"
        ))

        account_movements = self.movements.filter(is_active=True)[:10]
        for m in account_movements.all():
            if m.account_movement_type == ACCOUNTMOVEMENT_INVOICE:
                movement_type = _('Invoice')
            elif m.account_movement_type == ACCOUNTMOVEMENT_DEPOSIT:
                movement_type = _('Deposit')
            elif m.account_movement_type == ACCOUNTMOVEMENT_GRANDLODGEDEPOSIT:
                movement_type = _('Grand Lodge Deposit')
            elif m.account_movement_type == ACCOUNTMOVEMENT_CHARGE:
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
            last_movements_html += (
                "<tr>"
                "<td>%(date)s</td>"
                "<td>%(type)s</td>"
                "<td>%(amount)s</td>"
                "<td>%(balance)s</td>"
                "</tr>"
            ) % {
                'date': str(m.created_on.date()),
                'type': movement_type,
                'amount': str(m.amount),
                'balance': str(m.balance)
            }

        last_movements_html += "</tbody></table>"
        from_email = self.affiliation.lodge.treasurer.email
        send_mail(
            title,
            body + account_balance + last_movements,
            from_email,
            [self.affiliation.user.email],
            False,
            None,
            None,
            None,
            body_html + account_balance_html + last_movements_html
        )

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['affiliation']


LODGEACCOUNTMOVEMENT_INGRESS = 'I'
LODGEACCOUNTMOVEMENT_EGRESS = 'E'
LODGEACCOUNTMOVEMENT_TRANSFER = 'T'
LODGEACCOUNTMOVEMENT_DEPOSIT = 'D'
LODGEACCOUNT_MOVEMENT_TYPES = (
    (LODGEACCOUNTMOVEMENT_INGRESS, _('Ingress')),
    (LODGEACCOUNTMOVEMENT_EGRESS, _('Egress')),
    (LODGEACCOUNTMOVEMENT_TRANSFER, _('Transfer')),
    (LODGEACCOUNTMOVEMENT_DEPOSIT, _('Deposit'))
)


class LodgeAccountMovement(users.Model):
    """
    Logs every transaction between lodge accounts.
    """
    lodge_account = models.ForeignKey(
        LodgeAccount,
        verbose_name=_('lodge account'),
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
    balance = models.DecimalField(
        _('balance'),
        max_digits=15,
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

    def get_absolute_url(self):
        return reverse(
            'treasure:lodgeaccountmovement-detail', kwargs={'pk': self.pk}
        )

    class Meta:
        verbose_name = _('lodge account movement')
        verbose_name_plural = _('lodge account movements')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']


class LodgeAccountTransfer(users.Model):
    """
    Internal transfer between accounts.
    """
    lodge_account_from = models.ForeignKey(
        LodgeAccount,
        verbose_name=_('lodge account from'),
        related_name='transfers_from',
        related_query_name='transfer_from',
        on_delete=models.PROTECT,
        db_index=True
    )
    lodge_account_to = models.ForeignKey(
        LodgeAccount,
        verbose_name=_('lodge account to'),
        related_name='transfers_to',
        related_query_name='transfer_to',
        on_delete=models.PROTECT,
        db_index=True
    )
    description = models.CharField(
        _('description'),
        max_length=150,
        default="",
        blank=True
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return str(self.amount)

    def get_absolute_url(self):
        return reverse(
            'treasure:lodgeaccounttransfer-detail', kwargs={'pk': self.pk}
        )

    class Meta:
        verbose_name = _('lodge account transfer')
        verbose_name_plural = _('lodge account transfers')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']


ACCOUNTMOVEMENT_INVOICE = 'I'
ACCOUNTMOVEMENT_DEPOSIT = 'D'
ACCOUNTMOVEMENT_GRANDLODGEDEPOSIT = 'G'
ACCOUNTMOVEMENT_CHARGE = 'C'
ACCOUNT_MOVEMENT_TYPES = (
    (ACCOUNTMOVEMENT_INVOICE, _('Invoice')),
    (ACCOUNTMOVEMENT_DEPOSIT, _('Deposit')),
    (ACCOUNTMOVEMENT_GRANDLODGEDEPOSIT, _('Grand Lodge Deposit')),
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
    balance = models.DecimalField(
        _('balance'),
        max_digits=15,
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

    def get_absolute_url(self):
        return reverse(
            'treasure:accountmovement-detail', kwargs={'pk': self.pk}
        )

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
        _('begin'),
        help_text=_('YYYY-MM-DD')
    )
    end = models.DateField(
        _('end'),
        help_text=_('YYYY-MM-DD')
    )
    price_multiplier = models.PositiveSmallIntegerField(
        _('price multiplier'),
        default=1,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text=_(
            "Usually the category price is defined by a single unit price, "
            "but a period may have multiple units. For example, a unit can "
            "be a month, but a period could be 3, 4 or 12 months."
        )
    )
    send_email = models.BooleanField(
        _('send email'),
        default=False
    )

    def __str__(self):
        return str(self.begin) + ':' + str(self.end)

    def get_absolute_url(self):
        return reverse(
            'treasure:period-detail', kwargs={'pk': self.pk}
        )

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
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    account_movement = GenericRelation(
        AccountMovement,
        related_query_name='treasure_account_invoice',
        content_type_field='object_ct',
        object_id_field='object_id'
    )
    send_email = models.BooleanField(
        _('send email'),
        default=False
    )

    def __str__(self):
        return str(self.period) + ' $ ' + str(self.amount) + (
            ' (#' + str(self.id) + ')'
        )

    def get_absolute_url(self):
        return reverse('treasure:invoice-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']


class Deposit(users.Model):
    """
    A `payer` deposits money to one of the lodge accounts' handler.
    """
    payer = models.ForeignKey(
        users.Affiliation,
        verbose_name=_('payer'),
        related_name='deposits',
        related_query_name='deposit',
        on_delete=models.PROTECT,
        db_index=True
    )
    lodge_account = models.ForeignKey(
        LodgeAccount,
        verbose_name=_('lodge account'),
        related_name='deposits',
        related_query_name='deposit',
        on_delete=models.PROTECT,
        db_index=True
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
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
    send_email = models.BooleanField(
        _('send email'),
        default=False
    )

    def __str__(self):
        return str(self.payer) + '->' + (
            str(self.lodge_account.handler) + ' + $ ' + str(self.amount)
        ) + ' (#' + str(self.id) + ')'

    def get_absolute_url(self):
        return reverse('treasure:deposit-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('deposit')
        verbose_name_plural = _('deposits')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']


GRANDLODGEDEPOSIT_PENDING = 'P'
GRANDLODGEDEPOSIT_ACCREDITED = 'A'
GRANDLODGEDEPOSIT_REJECTED = 'R'
GRANDLODGEDEPOSIT_STATUSES = (
    (GRANDLODGEDEPOSIT_PENDING, _('Pending')),
    (GRANDLODGEDEPOSIT_ACCREDITED, _('Accredited')),
    (GRANDLODGEDEPOSIT_REJECTED, _('Rejected'))
)


class GrandLodgeDeposit(users.Model):
    """
    A `payer` deposits money directly to the Grand Lodge's bank account.
    Need to confirm it has been properly accredited by both the bank and the GL.
    """
    payer = models.ForeignKey(
        users.Affiliation,
        verbose_name=_('payer'),
        related_name='grand_lodge_deposits',
        related_query_name='grand_lodge_deposit',
        on_delete=models.PROTECT,
        db_index=True
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
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
    status = models.CharField(
        _('status'),
        max_length=1,
        choices=GRANDLODGEDEPOSIT_STATUSES,
        default=GRANDLODGEDEPOSIT_PENDING,
        blank=True
    )
    account_movement = GenericRelation(
        AccountMovement,
        related_query_name='treasure_account_grandlodgedeposit',
        content_type_field='object_ct',
        object_id_field='object_id'
    )
    send_email = models.BooleanField(
        _('send email'),
        default=False
    )

    def __str__(self):
        return str(self.payer) + ': $ ' + str(self.amount) + (
            ' (#' + str(self.id) + ')'
        )

    def get_absolute_url(self):
        return reverse(
            'treasure:grandlodgedeposit-detail', kwargs={'pk': self.pk}
        )

    class Meta:
        verbose_name = _('grand lodge deposit')
        verbose_name_plural = _('grand lodge deposits')
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
    An special ocassion charge, like an initiation, a raise, etc.
    """
    debtor = models.ForeignKey(
        users.Affiliation,
        verbose_name=_('debtor'),
        related_name='charges',
        related_query_name='charge',
        on_delete=models.PROTECT,
        db_index=True
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
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
    send_email = models.BooleanField(
        _('send email'),
        default=False
    )

    def __str__(self):
        return str(self.debtor) + ' - $ ' + str(self.amount) + (
            ' (#' + str(self.id) + ')'
        )

    def get_absolute_url(self):
        return reverse('treasure:charge-detail', kwargs={'pk': self.pk})

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
    Money that leaves the lodge.
    """
    lodge_account = models.ForeignKey(
        LodgeAccount,
        verbose_name=_('lodge account'),
        related_name='egresses',
        related_query_name='egress',
        on_delete=models.PROTECT,
        db_index=True
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
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

    def __str__(self):
        return str(self.lodge_account) + '- $ ' + str(self.amount)

    def get_absolute_url(self):
        return reverse(
            'treasure:lodgeaccountegress-detail', kwargs={'pk': self.pk}
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
    Money entering our lodge from the outside.
    """
    lodge_account = models.ForeignKey(
        LodgeAccount,
        verbose_name=_('lodge account'),
        related_name='ingresses',
        related_query_name='ingress',
        on_delete=models.PROTECT,
        db_index=True
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
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

    def __str__(self):
        return str(self.lodge_account) + '+ $ ' + str(self.amount)

    def get_absolute_url(self):
        return reverse(
            'treasure:lodgeaccountingress-detail', kwargs={'pk': self.pk}
        )

    class Meta:
        verbose_name = _('lodge account ingress')
        verbose_name_plural = _('lodge account ingresses')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']
