from django.db import models
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel
from juntagrico.util import temporal


class SubscriptionProduct(JuntagricoBaseModel):
    '''
    Product of subscription
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(
        _('Beschreibung'), max_length=1000, blank=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)
    is_extra = models.BooleanField(_('Ist Zusatzabo Produkt'), default=False)

    def __str__(self):
        return self.name

    @property
    def sizes_for_depot_list(self):
        return self.sizes.filter(depot_list=True).order_by('units')

    class Meta:
        verbose_name = _('{0}-Produkt').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{0}-Produkt').format(Config.vocabulary('subscription'))
        ordering = ['sort_order']


class SubscriptionSize(JuntagricoBaseModel):
    '''
    Subscription sizes
    '''
    name = models.CharField(_('Name'), max_length=100)
    long_name = models.CharField(_('Langer Name'), max_length=100)
    units = models.FloatField(_('Einheiten'))
    depot_list = models.BooleanField(
        _('Sichtbar auf Depotliste'), default=True)
    visible = models.BooleanField(_('Sichtbar'), default=True)
    description = models.TextField(
        _('Beschreibung'), max_length=1000, blank=True)
    product = models.ForeignKey('SubscriptionProduct', on_delete=models.PROTECT,
                                related_name='sizes', verbose_name=_('Produkt'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('{0}-Grösse').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{0}-Grössen').format(Config.vocabulary('subscription'))
        unique_together = ('name', 'product',)
        unique_together = ('units', 'product',)


class SubscriptionType(JuntagricoBaseModel):
    '''
    Subscription types
    '''
    name = models.CharField(_('Name'), max_length=100)
    long_name = models.CharField(_('Langer Name'), max_length=100, blank=True)
    size = models.ForeignKey('SubscriptionSize', on_delete=models.PROTECT,
                             related_name='types', verbose_name=_('Grösse'))
    shares = models.PositiveIntegerField(
        _('Anz benötigter Anteilsscheine'), default=0)
    required_assignments = models.PositiveIntegerField(
        _('Anz benötigter Arbeitseinsätze'))
    required_core_assignments = models.PositiveIntegerField(
        _('Anz benötigter Kern Arbeitseinsätze'), default=0)
    price = models.DecimalField(_('Preis'), max_digits=9, decimal_places=2)
    visible = models.BooleanField(_('Sichtbar'), default=True)
    trial = models.BooleanField(_('Probe-Abo'), default=False)
    trial_days = models.IntegerField(_('Probe-Abo Dauer in Tagen'), default=0)
    description = models.TextField(
        _('Beschreibung'), max_length=1000, blank=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    @property
    def has_periods(self):
        return self.periods.count() > 0

    def min_duration_info(self):
        if self.trial_days:
            return _('{} Tage. Keine automatische Verlängerung.').format(self.trial_days)
        if self.has_periods:
            return None  # price list already shows end of periods
        date = temporal.end_of_business_year()
        return _('Bis {day}.{month}. Automatische Verlängerung.').format(day=date.day, month=date.month)

    @property
    def display_name(self):
        name_parts = [self.size.product.name, self.size.name]
        if self.long_name:
            name_parts.append(self.long_name)
        return '-'.join(name_parts)

    def __str__(self):
        return self.name + ' - ' + _('Grösse') + ': ' + self.size.name + ' - ' + _('Produkt') + ': ' + self.size.product.name

    def __lt__(self, other):
        return self.pk < other.pk

    class Meta:
        verbose_name = _('{0}-Typ').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{0}-Typen').format(Config.vocabulary('subscription'))
        ordering = ['sort_order']
