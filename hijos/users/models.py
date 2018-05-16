from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
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
        return self.last_name + ', ' + self.first_name + (
            ' (' + self.degree + ')'
        )

    def get_absolute_url(self):
        return reverse('users:user-detail', kwargs={'username': self.username})

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
    treasurer = models.ForeignKey(
        User,
        verbose_name=_('treasurer'),
        related_name='+',
        related_query_name='+',
        on_delete=models.PROTECT,
        db_index=False,
        blank=True,
        null=True
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('users:lodge-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('lodge')
        verbose_name_plural = _('lodges')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['name']


class Category(Model):
    """
    Categories range from normal, discount for students, discount for under
    25yo, discount for multiple affiliations, etc.
    """
    name = models.CharField(
        _('name'),
        max_length=50,
        unique=True
    )
    description = models.CharField(
        _('description'),
        max_length=300,
        default="",
        blank=True
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('users:category-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['name']


class CategoryPrice(Model):
    """
    Prices are valid through a range of time.
    """
    category = models.ForeignKey(
        Category,
        verbose_name=_('category'),
        related_name='prices',
        related_query_name='price',
        on_delete=models.PROTECT,
        db_index=True
    )
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2
    )
    date_from = models.DateField(
        _('date from')
    )
    date_until = models.DateField(
        _('date until'),
        default=date(year=3000, month=12, day=31),
        blank=True
    )

    def __str__(self):
        return str(self.price) + ':' + (
            str(self.date_from) + '-' + str(self.date_until)
        )

    def get_absolute_url(self):
        return reverse('users:categoryprice-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('price')
        verbose_name_plural = _('prices')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-date_until', '-date_from']


class Affiliation(Model):
    """
    """
    lodge = models.ForeignKey(
        Lodge,
        verbose_name=_('lodge'),
        related_name='affiliations',
        related_query_name='affiliation',
        on_delete=models.PROTECT,
        db_index=True
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        related_name='affiliations',
        related_query_name='affiliation',
        on_delete=models.PROTECT,
        db_index=False
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_('category'),
        related_name='affiliations',
        related_query_name='affiliation',
        on_delete=models.PROTECT,
        db_index=False
    )

    def __str__(self):
        return str(self.user) + ' @ ' + str(self.lodge)

    def get_absolute_url(self):
        return reverse('users:affiliation-detail', kwargs={'pk': self.pk})

    def send_treasure_mail(self, title, content=""):
        if self.user.most_worshipful:
            body = _("Dear M.·.W.·.B.·. %(full_name)s:")
        elif self.user.worshipful:
            body = _("Dear W.·.B.·. %(full_name)s:")
        elif self.user.past_master:
            body = _("Dear P.·.M.·. %(full_name)s:")
        else:
            body = _("Dear B.·. %(full_name)s:")

        body = body % {'full_name': self.user.get_full_name()}
        body += "\n\t" + content + "\n\t"
        body += (
            "Your current account balance with %(lodge)s is of $ %(balance)s"
        ) % {
            'lodge': str(self.lodge),
            'balance': str(self.account.balance)
        }
        from_email = self.lodge.treasurer.email
        send_mail(title, body, from_email, [self.user.email])

    class Meta:
        index_together = ('lodge', 'user')
        unique_together = ('lodge', 'user')
        verbose_name = _('affiliation')
        verbose_name_plural = _('affiliations')
        default_permissions = ('add', 'change', 'delete', 'view')
        ordering = ['-created_on']
