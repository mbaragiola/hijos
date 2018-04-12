from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _


class UsersConfig(AppConfig):
    name = 'hijos.users'
    verbose_name = _("users")

    def ready(self):
        from hijos.users import models, signals

        post_save.connect(
            receiver=signals.lodge,
            sender=models.Lodge,
            dispatch_uid='Users_Lodge_CreateLodgeAccount',
            weak=False
        )
        post_save.connect(
            receiver=signals.affiliation,
            sender=models.Affiliation,
            dispatch_uid='Users_Affiliation_CreateAccount',
            weak=False
        )
