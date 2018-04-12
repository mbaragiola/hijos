from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from hijos.treasure import models


@admin.register(models.LodgeAccount)
class LodgeAccountAdmin(admin.ModelAdmin):
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


@admin.register(models.Charge)
class ChargeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.LodgeAccountIngress)
class LodgeAccountIngressAdmin(admin.ModelAdmin):
    pass


@admin.register(models.LodgeAccountEgress)
class LodgeAccountEgressAdmin(admin.ModelAdmin):
    pass
