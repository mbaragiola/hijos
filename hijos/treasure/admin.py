from django.contrib import admin

from hijos.treasure import models


@admin.register(models.LodgeGlobalAccount)
class LodgeGlobalAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(models.LodgeAccount)
class LodgeAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(models.LodgeAccountTransfer)
class LodgeAccountTransferAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(models.LodgeAccountMovement)
class LodgeAccountMovementAdmin(admin.ModelAdmin):
    pass


@admin.register(models.AccountMovement)
class AccountMovementAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Period)
class PeriodAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Deposit)
class DepositAdmin(admin.ModelAdmin):
    pass


@admin.register(models.GrandLodgeDeposit)
class GrandLodgeDepositAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Charge)
class ChargeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.LodgeAccountIngress)
class LodgeAccountIngressAdmin(admin.ModelAdmin):
    pass


@admin.register(models.LodgeAccountEgress)
class LodgeAccountEgressAdmin(admin.ModelAdmin):
    pass
