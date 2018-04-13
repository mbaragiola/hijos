from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _

from hijos.users import models


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = models.User


class MyUserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': _('This username has already been taken.')
    })

    class Meta(UserCreationForm.Meta):
        model = models.User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


@admin.register(models.User)
class MyUserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = (
        (_('User Profile'), {
            'fields': (
                'degree',
                'initiated',
                'passed',
                'raised',
                'past_master',
                'worshipful',
                'most_worshipful'
            )
        }),
    ) + AuthUserAdmin.fieldsets
    list_display = ('username', 'first_name', 'last_name', 'is_superuser')
    search_fields = ['username', 'first_name', 'last_name']


@admin.register(models.Lodge)
class LodgeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CategoryPrice)
class CategoryPriceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Affiliation)
class AffiliationAdmin(admin.ModelAdmin):
    pass
