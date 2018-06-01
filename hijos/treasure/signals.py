from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from hijos.treasure import models
from hijos.users import models as users


def period(sender, instance, created, raw, **kwargs):
    if created and not raw:
        affiliations = users.Affiliation.objects.filter(
            lodge=instance.lodge,
            is_active=True
        )
        for affiliation in affiliations.all():
            try:
                category_price = users.CategoryPrice.objects.get(
                    Q(category=affiliation.category),
                    Q(is_active=True),
                    Q(date_from__lte=instance.begin),
                    Q(date_until__gte=instance.begin),
                    Q(date_from__lte=instance.end),
                    Q(date_until__gte=instance.end)
                )
            except users.CategoryPrice.DoesNotExist:
                raise Exception(_("Category's price not found."))
            except users.CategoryPrice.MultipleObjectsReturned:
                raise Exception(_("More than one price found."))
            else:
                models.Invoice.objects.create(
                    period=instance,
                    affiliation=affiliation,
                    amount=category_price.price * instance.price_multiplier,
                    send_email=instance.send_email,
                    created_by=instance.created_by,
                    last_modified_by=instance.last_modified_by
                )


def invoice_and_charge(sender, instance, created, update_fields, raw, **kwargs):
    if created and not raw:
        if type(instance) is models.Invoice:
            affiliation = instance.affiliation
        elif type(instance) is models.Charge:
            affiliation = instance.debtor
        else:
            affiliation = ""

        account, new = models.Account.objects.get_or_create(
            affiliation=affiliation
        )
        if type(instance) is models.Invoice:
            account_movement_type = models.ACCOUNTMOVEMENT_INVOICE
            title = _("New invoice")
            content = _(
                "A new invoice has been issued to you for the period "
                "%(period)s of an amount $ %(amount)s."
            ) % {
                'period': str(instance.period),
                'amount': str(instance.amount)
            }
        elif type(instance) is models.Charge:
            account_movement_type = models.ACCOUNTMOVEMENT_CHARGE
            title = _("New charge")
            content = _(
                "A new charge has been issued to you of an amount $ %(amount)s."
            ) % {'amount': str(instance.amount)}
        else:
            raise Exception(_("Invalid account movement type."))

        models.AccountMovement.objects.create(
            content_object=instance,
            account=account,
            account_movement_type=account_movement_type,
            amount=-instance.amount,
            balance=account.balance - instance.amount,
            created_by=instance.created_by,
            last_modified_by=instance.last_modified_by
        )
        if instance.send_email:
            affiliation.account.send_treasure_mail(title, content)

    elif not created and update_fields and 'is_active' in update_fields:
        instance.account_movement.is_active = instance.is_active
        instance.account_movement.last_modified_by = instance.last_modified_by
        instance.account_movement.save(
            update_fields=('is_active', 'last_modified_by', 'last_modified_on')
        )


def deposit(sender, instance, created, update_fields, raw, **kwargs):
    if created and not raw:
        account, new = models.Account.objects.get_or_create(
            affiliation=instance.payer
        )

        models.AccountMovement.objects.create(
            content_object=instance,
            account=account,
            account_movement_type=models.ACCOUNTMOVEMENT_DEPOSIT,
            amount=instance.amount,
            balance=account.balance + instance.amount,
            created_by=instance.created_by,
            last_modified_by=instance.last_modified_by
        )
        models.LodgeAccountMovement.objects.create(
            content_object=instance,
            lodge_account=instance.lodge_account,
            lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_DEPOSIT,
            amount=instance.amount,
            balance=instance.lodge_account.balance + instance.amount,
            created_by=instance.created_by,
            last_modified_by=instance.last_modified_by
        )
        if instance.send_email:
            title = _("New deposit")
            content = _(
                "A new deposit on your behalf has been made of an amount "
                "$ %(amount)s."
            ) % {'amount': str(instance.amount)}
            instance.payer.account.send_treasure_mail(title, content)

    elif not created and update_fields and 'is_active' in update_fields:
        instance.account_movement.is_active = instance.is_active
        instance.account_movement.last_modified_by = instance.last_modified_by
        instance.account_movement.save(
            update_fields=('is_active', 'last_modified_by', 'last_modified_on')
        )
        instance.lodge_account_movement.is_active = instance.is_active
        instance.lodge_account_movement.last_modified_by = (
            instance.last_modified_by
        )
        instance.lodge_account_movement.save(
            update_fields=('is_active', 'last_modified_by', 'last_modified_on')
        )


def account_movement(sender, instance, created, update_fields, raw, **kwargs):
    if created and not raw:
        instance.account.balance += instance.amount
    elif not created and update_fields and 'is_active' in update_fields:
        instance.account.balance += -instance.amount

    instance.account.last_modified_by = instance.last_modified_by
    instance.account.save(
        update_fields=('balance', 'last_modified_by', 'last_modified_on')
    )


def lodge_account_movement(
    sender, instance, created, update_fields, raw, **kwargs
):
    lodge_global_account = (
        instance.lodge_account.handler.lodge.lodge_global_account
    )
    if created and not raw:
        instance.lodge_account.balance += instance.amount
        lodge_global_account.balance += instance.amount
    elif not created and update_fields and 'is_active' in update_fields:
        instance.lodge_account.balance += -instance.amount
        lodge_global_account.balance += -instance.amount

    instance.lodge_account.last_modified_by = instance.last_modified_by
    instance.lodge_account.save(
        update_fields=('balance', 'last_modified_by', 'last_modified_on')
    )
    lodge_global_account.last_modified_by = instance.last_modified_by
    lodge_global_account.save(
        update_fields=('balance', 'last_modified_by', 'last_modified_on')
    )


def grand_lodge_deposit(sender, instance, created, update_fields, **kwargs):
    if not created and update_fields and 'status' in update_fields:
        account, new = models.Account.objects.get_or_create(
            affiliation=instance.payer
        )

        if instance.status == models.GRANDLODGEDEPOSIT_ACCREDITED:
            models.AccountMovement.objects.create(
                content_object=instance,
                account=account,
                account_movement_type=models.ACCOUNTMOVEMENT_GRANDLODGEDEPOSIT,
                amount=instance.amount,
                balance=account.balance + instance.amount,
                created_by=instance.created_by,
                last_modified_by=instance.last_modified_by
            )


def lodge_account_ingress_and_egress(
    sender, instance, created, update_fields, raw, **kwargs
):
    if created and not raw:
        if type(instance) is models.LodgeAccountIngress:
            models.LodgeAccountMovement.objects.create(
                content_object=instance,
                lodge_account=instance.lodge_account,
                lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_INGRESS,
                amount=instance.amount,
                balance=instance.lodge_account.balance + instance.amount,
                created_by=instance.created_by,
                last_modified_by=instance.last_modified_by
            )
        elif type(instance) is models.LodgeAccountEgress:
            models.LodgeAccountMovement.objects.create(
                content_object=instance,
                lodge_account=instance.lodge_account,
                lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_EGRESS,
                amount=-instance.amount,
                balance=instance.lodge_account.balance - instance.amount,
                created_by=instance.created_by,
                last_modified_by=instance.last_modified_by
            )
    elif not created and update_fields and 'is_active' in update_fields:
        instance.lodge_account_movement.is_active = instance.is_active
        instance.lodge_account_movement.last_modified_by = (
            instance.last_modified_by
        )
        instance.lodge_account_movement.save(
            update_fields=('is_active', 'last_modified_by', 'last_modified_on')
        )


def lodge_account_transfer(
    sender, instance, created, update_fields, raw, **kwargs
):
    if created and not raw:
        models.LodgeAccountMovement.objects.create(
            content_object=instance,
            lodge_account=instance.lodge_account_from,
            lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_TRANSFER,
            amount=-instance.amount,
            balance=instance.lodge_account_from.balance - instance.amount,
            created_by=instance.created_by,
            last_modified_by=instance.last_modified_by
        )
        models.LodgeAccountMovement.objects.create(
            content_object=instance,
            lodge_account=instance.lodge_account_to,
            lodgeaccount_movement_type=models.LODGEACCOUNTMOVEMENT_TRANSFER,
            amount=instance.amount,
            balance=instance.lodge_account_to.balance + instance.amount,
            created_by=instance.created_by,
            last_modified_by=instance.last_modified_by
        )
    elif not created and update_fields and 'is_active' in update_fields:
        instance.lodge_account_movement_from.is_active = instance.is_active
        instance.lodge_account_movement_from.last_modified_by = (
            instance.last_modified_by
        )
        instance.lodge_account_movement_from.save(
            update_fields=('is_active', 'last_modified_by', 'last_modified_on')
        )
        instance.lodge_account_movement_to.is_active = instance.is_active
        instance.lodge_account_movement_to.last_modified_by = (
            instance.last_modified_by
        )
        instance.lodge_account_movement_to.save(
            update_fields=('is_active', 'last_modified_by', 'last_modified_on')
        )
