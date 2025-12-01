from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel
from juntagrico.queryset.subtypes import SubscriptionTypeQueryset, ProductSizeQueryset, SubscriptionProductQueryset
from juntagrico.util import temporal


class SubscriptionProduct(JuntagricoBaseModel):
    '''
    Product of subscription
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(_('Beschreibung'), blank=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    objects = SubscriptionProductQueryset.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('{0}-Produkt').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{0}-Produkt').format(Config.vocabulary('subscription'))
        ordering = ['sort_order']


class ProductSize(JuntagricoBaseModel):
    """
    Items inside a subscription bundle
    """
    name = models.CharField(_('Name'), max_length=100)
    units = models.FloatField(_('Einheiten'), default=1.0)
    show_on_depot_list = models.BooleanField(_('Sichtbar auf Depotliste'), default=True)
    product = models.ForeignKey('SubscriptionProduct', on_delete=models.CASCADE, related_name='sizes', verbose_name=_('Produkt'))

    objects = ProductSizeQueryset.as_manager()

    def __str__(self):
        return f'{self.name} {self.product.name}'

    class Meta:
        verbose_name = _('Produktgrösse')
        verbose_name_plural = _('Produktgrössen')
        constraints = [
            models.UniqueConstraint(fields=['name', 'product'], name='unique_name_product'),
        ]


class SubscriptionBundleProductSize(models.Model):
    # through model is needed to allow duplicate m2m relationships
    bundle = models.ForeignKey('SubscriptionBundle', on_delete=models.CASCADE)
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)


class SubscriptionCategory(JuntagricoBaseModel):
    """
    category of subscription for grouping in order process
    """
    name = models.CharField(_('Name'), max_length=100, unique=True, blank=True)
    description = models.TextField(_('Beschreibung'), blank=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    def __str__(self):
        return self.name or _('(Ohne Namen)')

    class Meta:
        verbose_name = _('{0}-Kategorie').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{0}-Kategorie').format(Config.vocabulary('subscription'))
        ordering = ['sort_order']


# TODO: Rename all instances from size to bundle
class SubscriptionBundle(JuntagricoBaseModel):
    '''
    Subscription Bundle
    '''
    long_name = models.CharField(_('Langer Name'), max_length=100)
    description = models.TextField(_('Beschreibung'), blank=True)
    category = models.ForeignKey('SubscriptionCategory', on_delete=models.SET_NULL,
                                 related_name='bundles', verbose_name=_('Kategorie'), null=True, blank=True,
                                 help_text=_('Wenn leer, kann dieses Paket nicht bestellt werden.'))
    product_sizes = models.ManyToManyField(
        'ProductSize', related_name='bundles', verbose_name=_('Produktgrössen'),
        through=SubscriptionBundleProductSize
    )

    def __str__(self):
        return f'{self.category or _("(Nicht Bestellbar)")} - {self.long_name}'

    class Meta:
        verbose_name = _('{0}-Grösse').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{0}-Grössen').format(Config.vocabulary('subscription'))


class SubscriptionType(JuntagricoBaseModel):
    '''
    Subscription types
    '''
    name = models.CharField(_('Name'), max_length=100)
    long_name = models.CharField(_('Langer Name'), max_length=100, blank=True)
    bundle = models.ForeignKey('SubscriptionBundle', on_delete=models.PROTECT,
                               related_name='types', verbose_name=_('Grösse'))
    shares = models.PositiveIntegerField(
        _('Anz benötigter Anteilsscheine'), default=0)
    required_assignments = models.FloatField(_('Anz benötigter Arbeitseinsätze'))
    required_core_assignments = models.FloatField(_('Anz benötigter Kern Arbeitseinsätze'), default=0)
    price = models.DecimalField(_('Preis'), max_digits=9, decimal_places=2)
    visible = models.BooleanField(_('Sichtbar'), default=True)
    is_extra = models.BooleanField(_('Ist Zusatzabo'), default=False)
    trial = models.BooleanField(_('Probe-Abo'), default=False)  # Deprecated
    trial_days = models.IntegerField(_('Probe-Abo Dauer in Tagen'), default=0)
    description = models.TextField(_('Beschreibung'), blank=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)
    # Interval of the subscription (e.g 2 for every 2 weeks)
    interval = models.PositiveIntegerField(_('Intervall'), default=1, blank=False, null=False,
                                           validators=[MinValueValidator(1)],
                                           help_text=_('Intervall der Lieferung in Wochen,'
                                                       '1 heisst jede Woche, 2 heisst alle 2 Wochen, usw.'))
    offset = models.PositiveIntegerField(_('Versatz'), default=0, blank=False, null=False,
                                         help_text=_('Versatz der Lieferung in Wochen, '
                                                     '0 entspricht einer Lieferung ab der ersten Kalenderwoche, '
                                                     '1 entspricht einer Lieferung ab der zweiten Kalenderwoche, usw.'))

    objects = SubscriptionTypeQueryset.as_manager()

    @property
    def has_periods(self):
        return self.periods.count() > 0

    def min_duration_info(self):
        if self.trial_days:
            return _('Für {} Tage. Keine automatische Verlängerung.').format(self.trial_days)
        if self.has_periods:
            return None  # price list already shows end of periods
        date = temporal.end_of_business_year()
        return _('Bis {day}.{month}. Automatische Verlängerung.').format(day=date.day, month=date.month)

    @property
    def display_name(self):
        return '-'.join([str(self.bundle), self.long_name])

    def __str__(self):
        return '-'.join([str(self.bundle), self.name])

    def __lt__(self, other):
        return self.pk < other.pk

    class Meta:
        verbose_name = _('{0}-Typ').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{0}-Typen').format(Config.vocabulary('subscription'))
        ordering = ['sort_order']
