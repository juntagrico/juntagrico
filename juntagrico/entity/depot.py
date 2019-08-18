from django.core import validators
from django.db import models
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.dao.extrasubscriptioncategorydao \
    import ExtraSubscriptionCategoryDao
from juntagrico.dao.extrasubscriptiontypedao import ExtraSubscriptionTypeDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao
from juntagrico.entity import JuntagricoBaseModel
from juntagrico.util.temporal import weekday_choices, weekdays


class Depot(JuntagricoBaseModel):
    '''
    Location where stuff is picked up.
    '''
    code = models.CharField(_('Sortier-Code'), max_length=100,
                            validators=[validators.validate_slug], unique=True)
    name = models.CharField(_('{0} Name').format(Config.vocabulary('depot')), max_length=100, unique=True)
    contact = models.ForeignKey('Member', on_delete=models.PROTECT)
    weekday = models.PositiveIntegerField(_('Wochentag'), choices=weekday_choices)
    capacity = models.PositiveIntegerField(_('Kapazität'), default=0)
    latitude = models.CharField(_('Latitude'), max_length=100, default='',
                                null=True, blank=True)
    longitude = models.CharField(_('Longitude'), max_length=100, default='',
                                 null=True, blank=True)
    addr_street = models.CharField(_('Strasse'), max_length=100,
                                   null=True, blank=True)
    addr_zipcode = models.CharField(_('PLZ'), max_length=10,
                                    null=True, blank=True)
    addr_location = models.CharField(_('Ort'), max_length=50,
                                     null=True, blank=True)
    description = models.TextField(_('Beschreibung'), max_length=1000, default='')

    overview_cache = None
    subscription_cache = None

    def __str__(self):
        return '%s %s' % (self.id, self.name)

    def active_subscriptions(self):
        return self.subscription_set.filter(active=True)

    @property
    def has_geo(self):
        lat = self.latitude is not None and self.latitude != ''
        long = self.longitude is not None and self.longitude != ''
        street = self.addr_street is not None and self.addr_street != ''
        zip = self.addr_zipcode is not None and self.addr_zipcode != ''
        loc = self.addr_location is not None and self.addr_location != ''
        return lat and long and street and zip and loc

    @property
    def weekday_name(self):
        day = _('Unbekannt')
        if 8 > self.weekday > 0:
            day = weekdays[self.weekday]
        return day

    @staticmethod
    def subscription_amounts(subscriptions, id):
        amount = 0
        for subscription in subscriptions.all():
            amount += subscription.subscription_amount(id)
        return amount

    @staticmethod
    def extra_subscription(subscriptions, code):
        amount = 0
        for subscription in subscriptions.all():
            esubs = subscription.extra_subscriptions.all()
            filtered_esubs = esubs.filter(type__name=code)
            amount += len(filtered_esubs)
        return amount

    def fill_overview_cache(self):
        self.fill_active_subscription_cache()
        self.overview_cache = []
        for product in SubscriptionProductDao.get_all():
            for subscription_size in SubscriptionSizeDao.sizes_for_depot_list_by_product(product):
                cache = self.subscription_cache
                size_id = subscription_size.id
                amounts = self.subscription_amounts(cache, size_id)
                self.overview_cache.append(amounts)
        for category in ExtraSubscriptionCategoryDao.all_categories_ordered():
            types = ExtraSubscriptionTypeDao.extra_types_by_category_ordered(
                category)
            for extra_subscription in types:
                code = extra_subscription.name
                cache = self.subscription_cache
                esub = self.extra_subscription(cache, code)
                self.overview_cache.append(esub)

    def fill_active_subscription_cache(self):
        self.subscription_cache = self.active_subscriptions()

    class Meta:
        verbose_name = Config.vocabulary('depot')
        verbose_name_plural = Config.vocabulary('depot_pl')
        permissions = (('is_depot_admin', _('Benutzer ist Depot Admin')),)
