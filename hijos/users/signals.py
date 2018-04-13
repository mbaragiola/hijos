from hijos.treasure import models as treasure


def lodge(sender, instance, created, **kwargs):
    if created:
        treasure.LodgeGlobalAccount.objects.create(
            lodge=instance,
            created_by=instance.created_by,
            last_modified_by=instance.created_by
        )


def affiliation(sender, instance, created, **kwargs):
    if created:
        treasure.Account.objects.create(
            affiliation=instance,
            created_by=instance.created_by,
            last_modified_by=instance.created_by
        )
