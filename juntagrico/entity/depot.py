# encoding: utf-8

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from juntagrico.util.temporal import *

from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao
from juntagrico.dao.extrasubscriptiontypedao import ExtraSubscriptionTypeDao
from juntagrico.dao.extrasubscriptioncategorydao import ExtraSubscriptionCategoryDao

class Depot(models.Model):
    '''
    Location where stuff is picked up.
    '''
    code = models.CharField('Code', max_length=100, validators=[validators.validate_slug], unique=True)
    name = models.CharField('Depot Name', max_length=100, unique=True)
    contact = models.ForeignKey('Member', on_delete=models.PROTECT)
    weekday = models.PositiveIntegerField('Wochentag', choices=weekday_choices)
    latitude = models.CharField('Latitude', max_length=100, default='')
    longitude = models.CharField('Longitude', max_length=100, default='')

    addr_street = models.CharField('Strasse', max_length=100)
    addr_zipcode = models.CharField('PLZ', max_length=10)
    addr_location = models.CharField('Ort', max_length=50)

    description = models.TextField('Beschreibung', max_length=1000, default='')

    overview_cache = None
    subscription_cache = None

    def __str__(self):
        return '%s %s' % (self.id, self.name)

    def active_subscriptions(self):
        return self.subscription_set.filter(active=True)

    @property
    def weekday_name(self):
        day = 'Unbekannt'
        if 8 > self.weekday > 0:
            day = weekdays[self.weekday]
        return day

    @staticmethod
    def subscription_amounts(subscriptions, name):
        amount = 0
        for subscription in subscriptions.all():
            amount += subscription.subscription_amount(name)
        return amount

    @staticmethod
    def extra_subscription(subscriptions, code):
        amount = 0
        for subscription in subscriptions.all():
            amount += len(subscription.extra_subscriptions.all().filter(type__name=code))
        return amount

    def fill_overview_cache(self):
        self.fill_active_subscription_cache()
        self.overview_cache = []
        for subscription_size in SubscriptionSizeDao.sizes_for_depot_list():
            self.overview_cache.append(self.subscription_amounts(self.subscription_cache, subscription_size.name))
        for category in ExtraSubscriptionCategoryDao.all_categories_ordered():
            for extra_subscription in ExtraSubscriptionTypeDao.extra_types_by_category_ordered(category):
                code = extra_subscription.name
                self.overview_cache.append(self.extra_subscription(self.subscription_cache, code))

    def fill_active_subscription_cache(self):
        self.subscription_cache = self.active_subscriptions()

    class Meta:
        verbose_name = 'Depot'
        verbose_name_plural = 'Depots'
        permissions = (('is_depot_admin', 'Benutzer ist Depot Admin'),)
