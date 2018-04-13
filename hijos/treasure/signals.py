from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from hijos.treasure import models
from hijos.users import models as users


def period(sender, instance, created, **kwargs):
    if created:
        affiliations = users.Affiliation.objects.filter(
            lodge=instance.lodge,
            is_active=True
        )
        today = timezone.now().date()
        for affiliation in affiliations.all():
            try:
                category_price = models.CategoryPrice.objects.get(
                    category=affiliation.category,
                    is_active=True,
                    date_from__lte=today,
                    date_until__gte=today
                )
            except models.CategoryPrice.DoesNotExist:
                raise Exception(_("Category's price not found."))
            except models.CategoryPrice.MultipleObjectsReturned:
                raise Exception(_("More than one price found."))
            else:
                models.Invoice.objects.create(
                    period=instance,
                    affiliation=affiliation,
                    amount=category_price.price,
                    created_by=instance.created_by,
                    last_modified_by=instance.last_modified_by
                )


def invoice_and_charge(sender, instance, created, update_fields, **kwargs):
    if created:
        account, new = models.Account.objects.get_or_create(
            affiliation=instance.affiliation
        )
        if type(instance) is models.Invoice:
            account_movement_type = models.ACCOUNTMOVEMENT_INVOICE
        elif type(instance) is models.Charge:
            account_movement_type = models.ACCOUNTMOVEMENT_CHARGE
        else:
            raise Exception(_("Invalid account movement type."))

        models.AccountMovement.objects.create(
            account=account,
            account_movement_type=account_movement_type,
            amount=-instance.amount,
            balance=account.balance - instance.amount,
            created_by=instance.created_by,
            last_modified_by=instance.last_modified_by
        )
    elif not created and 'is_active' in update_fields:
        instance.account_movement.is_active = instance.is_active
        instance.account_movement.last_modified_by = instance.last_modified_by
        instance.account_movement.save(
            update_fields=('is_active', 'last_modified_by', 'last_modified_on')
        )


def deposit(sender, instance, created, update_fields, **kwargs):
    if created:
        account, new = models.Account.objects.get_or_create(
            affiliation=instance.payer
        )

        models.AccountMovement.objects.create(
            account=account,
            account_movement_type=models.ACCOUNTMOVEMENT_DEPOSIT,
            amount=instance.amount,
            balance=account.balance + instance.amount,
            created_by=instance.created_by,
            last_modified_by=instance.last_modified_by
        )
        models.LodgeAccountMovement.objects.create(
            lodge_account=instance.lodge_account,
            account_movement_type=models.LODGEACCOUNTMOVEMENT_DEPOSIT,
            amount=instance.amount,
            balance=instance.lodge_account.balance + instance.amount,
            created_by=instance.created_by,
            last_modified_by=instance.last_modified_by
        )
    elif not created and 'is_active' in update_fields:
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


def account_movement(sender, instance, created, update_fields, **kwargs):
    if created:
        instance.account.balance += instance.amount
    elif not created and 'is_active' in update_fields:
        instance.account.balance += -instance.amount

    instance.account.last_modified_by = instance.last_modified_by
    instance.account.save(
        update_fields=('balance', 'last_modified_by', 'last_modified_on')
    )


def lodge_account_movement(sender, instance, created, update_fields, **kwargs):
    global_lodge_account = (
        instance.lodge_account.handler.lodge.global_lodge_account
    )
    if created:
        instance.lodge_account.balance += instance.amount
        global_lodge_account.balance += instance.amount
    elif not created and 'is_active' in update_fields:
        instance.lodge_account.balance += -instance.amount
        global_lodge_account.balance += -instance.amount

    instance.lodge_account.last_modified_by = instance.last_modified_by
    instance.lodge_account.save(
        update_fields=('balance', 'last_modified_by', 'last_modified_on')
    )
    global_lodge_account.last_modified_by = instance.last_modified_by
    global_lodge_account.save(
        update_fields=('balance', 'last_modified_by', 'last_modified_on')
    )


def grand_lodge_deposit(sender, instance, created, update_fields, **kwargs):
    if not created and 'status' in update_fields:
        account, new = models.Account.objects.get_or_create(
            affiliation=instance.payer
        )

        if instance.status == models.GRANDLODGEDEPOSIT_ACCREDITED:
            models.AccountMovement.objects.create(
                account=account,
                account_movement_type=models.ACCOUNTMOVEMENT_GRANDLODGEDEPOSIT,
                amount=instance.amount,
                balance=account.balance + instance.amount,
                created_by=instance.created_by,
                last_modified_by=instance.last_modified_by
            )
