from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _


class TreasureConfig(AppConfig):
    name = 'treasure'
    verbose_name = _('treasure')

    def ready(self):
        from hijos.treasure import models, signals

        post_save.connect(
            receiver=signals.period,
            sender=models.Period,
            dispatch_uid='Treasure_Period_CreateInvoices',
            weak=False
        )
        post_save.connect(
            receiver=signals.invoice_and_charge,
            sender=models.Invoice,
            dispatch_uid='Treasure_Invoice_SyncAccountMovement',
            weak=False
        )
        post_save.connect(
            receiver=signals.invoice_and_charge,
            sender=models.Charge,
            dispatch_uid='Treasure_Charge_SyncAccountMovement',
            weak=False
        )
        post_save.connect(
            receiver=signals.deposit,
            sender=models.Deposit,
            dispatch_uid='Treasure_Deposit_SyncAccountAndLodgeAccountMovement',
            weak=False
        )
        post_save.connect(
            receiver=signals.account_movement,
            sender=models.AccountMovement,
            dispatch_uid='Treasure_AccountMovement_SyncAccount',
            weak=False
        )
        post_save.connect(
            receiver=signals.lodge_account_movement,
            sender=models.LodgeAccountMovement,
            dispatch_uid='Treasure_LodgeAccountMovement_SyncLodgeAccount',
            weak=False
        )
