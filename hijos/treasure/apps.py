from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _


class TreasureConfig(AppConfig):
    name = 'hijos.treasure'
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
        post_save.connect(
            receiver=signals.lodge_account_ingress_and_egress,
            sender=models.LodgeAccountIngress,
            dispatch_uid=(
                'Treasure_LodgeAccountIngress_SyncLodgeAccountMovement'
            ),
            weak=False
        )
        post_save.connect(
            receiver=signals.lodge_account_ingress_and_egress,
            sender=models.LodgeAccountEgress,
            dispatch_uid=(
                'Treasure_LodgeAccountEgress_SyncLodgeAccountMovement'
            ),
            weak=False
        )
        post_save.connect(
            receiver=signals.lodge_account_transfer,
            sender=models.LodgeAccountTransfer,
            dispatch_uid=(
                'Treasure_LodgeAccountTransfer_SyncLodgeAccountMovement'
            ),
            weak=False
        )
        post_save.connect(
            receiver=signals.grand_lodge_deposit,
            sender=models.GrandLodgeDeposit,
            dispatch_uid=(
                'Treasure_GrandLodgeDeposit_SyncAccount'
            ),
            weak=False
        )
