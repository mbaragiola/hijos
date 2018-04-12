from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

from hijos.treasure import models
from hijos.users import models as users


def period(sender, instance, created, **kwargs):
    if created:
        affiliations = users.Affiliation.objects.filter(
            lodge=instance.lodge,
            is_active=True
        )
        for affiliation in affiliations.all():
            if affiliation.affiliation_type == users.AFFILIATION_SIMPLE:
                amount = instance.simple_affiliation_amount
            elif affiliation.affiliation_type == users.AFFILIATION_MULTIPLE:
                amount = instance.multiple_affiliation_amount
            else:
                raise Exception(_("Invalid affiliation type."))

            models.Invoice.objects.create(
                period=instance,
                affiliation=affiliation,
                amount=amount,
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
            affiliation=instance.affiliation
        )

        models.AccountMovement.objects.create(
            account=account,
            account_movement_type=models.ACCOUNTMOVEMENT_DEPOSIT,
            amount=instance.amount,
            created_by=instance.created_by,
            last_modified_by=instance.last_modified_by
        )
        try:
            lodge_account = models.LodgeAccount.get(
                lodge=instance.affiliation.lodge,
                code='001'
            )
        except models.LodgeAccount.DoesNotExist:
            raise Exception(_("Lodge account not found."))
        else:
            models.LodgeAccountMovement.objects.create(
                lodge_account=lodge_account,
                account_movement_type=models.LODGEACCOUNTMOVEMENT_DEPOSIT,
                amount=instance.amount,
                created_by=instance.created_by,
                last_modified_by=instance.last_modified_by
            )
    elif not created and 'is_active' in update_fields:
        instance.account_movement.is_active = instance.is_active
        instance.account_movement.last_modified_by = instance.last_modified_by
        instance.account_movement.save(
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
    if created:
        instance.lodge_account.balance += instance.amount
    elif not created and 'is_active' in update_fields:
        instance.lodge_account.balance += -instance.amount

    instance.lodge_account.last_modified_by = instance.last_modified_by
    instance.lodge_account.save(
        update_fields=('balance', 'last_modified_by', 'last_modified_on')
    )
