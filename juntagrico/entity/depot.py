from django.db import models
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel, absolute_url
from juntagrico.entity.location import Location
from juntagrico.util.models import q_isactive
from juntagrico.util.temporal import weekday_choices, weekdays


@absolute_url(name='tour')
class Tour(JuntagricoBaseModel):
    """
    Delivery Tour to depots
    """
    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(_('Beschreibung'), default='', blank=True)
    visible_on_list = models.BooleanField(_('Sichtbar auf Listen'), default=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    def __str__(self):
        return self.name

    def subscriptions(self):
        from juntagrico.entity.subs import Subscription
        return Subscription.objects.filter(depot__tour=self)

    class Meta:
        verbose_name = _('Ausfahrt')
        verbose_name_plural = _('Ausfahrten')
        ordering = ['sort_order']


@absolute_url(name='depot')
class Depot(JuntagricoBaseModel):
    '''
    Location where stuff is picked up.
    '''
    name = models.CharField(_('{0} Name').format(Config.vocabulary('depot')), max_length=100, unique=True)
    contact = models.ForeignKey('Member', on_delete=models.PROTECT)
    weekday = models.PositiveIntegerField(_('Wochentag'), choices=weekday_choices)
    tour = models.ForeignKey(Tour, on_delete=models.PROTECT, related_name='depots',
                             verbose_name=_('Ausfahrt'), blank=True, null=True)
    capacity = models.PositiveIntegerField(_('Kapazität'), default=0)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, verbose_name=_('Ort'))
    fee = models.DecimalField(_('Aufpreis'), max_digits=9, decimal_places=2, default=0.0,
                              help_text=_('Aufpreis für {0}').format(Config.vocabulary('member')))
    description = models.TextField(_('Beschreibung'), default='', blank=True)
    access_information = models.TextField(_('Zugangsbeschreibung'), default='',
                                          help_text=_('Nur für {0} des/r {1} sichtbar')
                                          .format(Config.vocabulary('member_pl'),
                                                  Config.vocabulary('depot')))
    depot_list = models.BooleanField(_('Sichtbar auf Depotliste'), default=True)
    visible = models.BooleanField(_('Sichtbar'), default=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    overview_cache = None
    subscription_cache = None

    def __str__(self):
        return '%s %s' % (self.id, self.name)

    def active_subscriptions(self):
        return self.subscription_set.filter(q_isactive()).order_by('primary_member__first_name',
                                                                   'primary_member__last_name')

    @property
    def map_info(self):
        map_info = self.location.map_info
        map_info['name'] = self.name
        map_info['id'] = self.id
        return map_info

    @property
    def weekday_name(self):
        if 8 > self.weekday > 0:
            return weekdays[self.weekday]
        return _('Unbekannt')

    def total_fee(self, subscription_count):
        """
        :param subscription_count: a dict of subscription_type => amount
        :return: total fee for this depot with selected subscription.
        """
        fee = self.fee
        conditions = self.subscription_type_conditions.filter(subscription_type__in=subscription_count.keys())
        for condition in conditions:
            fee += condition.fee * subscription_count[condition.subscription_type]
        return fee

    class Meta:
        verbose_name = Config.vocabulary('depot')
        verbose_name_plural = Config.vocabulary('depot_pl')
        ordering = ['sort_order']
        permissions = (('is_depot_admin', _('Benutzer ist Depot Admin')),)


class DepotSubscriptionTypeCondition(JuntagricoBaseModel):
    depot = models.ForeignKey('Depot', on_delete=models.CASCADE, verbose_name=Config.vocabulary('depot'),
                              related_name='subscription_type_conditions')
    subscription_type = models.ForeignKey('SubscriptionType', on_delete=models.CASCADE,
                                          verbose_name=_('{0}-Typ').format(Config.vocabulary('subscription')),
                                          related_name='depot_conditions')
    fee = models.DecimalField(_('Aufpreis'), max_digits=9, decimal_places=2, default=0.0,
                              help_text=_('Aufpreis für {0}').format(Config.vocabulary('member')))

    def __str__(self):
        return f"{self.depot} - {self.subscription_type}: "

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['depot', 'subscription_type'], name='unique_depot_subscription_type'),
        ]
        verbose_name = _('{0}-{1}-Typ').format(Config.vocabulary('depot'), Config.vocabulary('subscription'))
        verbose_name_plural = _('{0}-{1}-Typen').format(Config.vocabulary('depot'), Config.vocabulary('subscription'))
