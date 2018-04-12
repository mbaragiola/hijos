from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

DEGREE_ENTEREDAPPRENTICE = '1'
DEGREE_FELLOWCRAFT = '2'
DEGREE_MASTERMASON = '3'
DEGREES = (
    (DEGREE_ENTEREDAPPRENTICE, _('Entered Apprentice')),
    (DEGREE_FELLOWCRAFT, _('Fellow Craft')),
    (DEGREE_MASTERMASON, _('Master Mason'))
)

AFFILIATION_SIMPLE = 'S'
AFFILIATION_MULTIPLE = 'M'
AFFILIATIONS = (
    (AFFILIATION_SIMPLE, _('Simple')),
    (AFFILIATION_MULTIPLE, _('Multiple'))
)


class User(AbstractUser):
    """
    """
    degree = models.CharField(
        _('degree'),
        max_length=1,
        choices=DEGREES,
        default=DEGREE_ENTEREDAPPRENTICE
    )
    initiated = models.DateField(
        _('initiated'),
        blank=True,
        null=True,
        help_text=_("Initiation date.")
    )
    passed = models.DateField(
        _('passed'),
        blank=True,
        null=True,
        help_text=_("Passed to Fellow Craft date.")
    )
    raised = models.DateField(
        _('raised'),
        blank=True,
        null=True,
        help_text=_("Raised to Master Mason date.")
    )
    past_master = models.BooleanField(
        _('past master'),
        default=False,
        blank=True,
        help_text=_("Is or was Worshipful Master.")
    )
    worshipful = models.BooleanField(
        _('worshipful'),
        default=False,
        blank=True,
        help_text=_("Is or was elected official of the Grand Lodge.")
    )
    most_worshipful = models.BooleanField(
        _('most worshipful'),
        default=False,
        blank=True,
        help_text=_(
            "Is or was elected as Most Worshipful Master of the Grand Lodge."
        )
    )

    def __str__(self):
        return self.last_name + ', ' + self.first_name

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['last_name', 'first_name']


class Model(models.Model):
    """
    """
    id = models.BigAutoField(
        primary_key=True,
        editable=False
    )
    is_active = models.BooleanField(
        _('is active?'),
        default=True
    )
    created_on = models.DateTimeField(
        _('created on'),
        auto_now_add=True
    )
    last_modified_on = models.DateTimeField(
        _('last modified on'),
        auto_now=True
    )
    created_by = models.ForeignKey(
        User,
        verbose_name=_('created by'),
        related_name='+',
        related_query_name='+',
        on_delete=models.PROTECT,
        db_index=False
    )
    last_modified_by = models.ForeignKey(
        User,
        verbose_name=_('last modified by'),
        related_name='+',
        related_query_name='+',
        on_delete=models.PROTECT,
        db_index=False
    )

    class Meta:
        abstract = True


class Lodge(Model):
    """
    """
    name = models.CharField(
        _('name'),
        max_length=150,
        unique=True
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _('lodge')
        verbose_name_plural = _('lodges')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['name']


class Affiliation(Model):
    """
    """
    lodge = models.ForeignKey(
        Lodge,
        verbose_name=_('lodge'),
        related_name='affiliations',
        related_query_name='affiliation',
        on_delete=models.PROTECT
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        related_name='affiliations',
        related_query_name='affiliation',
        on_delete=models.PROTECT
    )
    affiliation_type = models.CharField(
        _('affiliation type'),
        max_length=1,
        choices=AFFILIATIONS
    )

    def __str__(self):
        return str(self.user) + ' @ ' + str(self.lodge)

    class Meta:
        index_together = ('lodge', 'user')
        unique_together = ('lodge', 'user')
        verbose_name = _('affiliation')
        verbose_name_plural = _('affiliations')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']
