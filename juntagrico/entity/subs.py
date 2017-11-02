# encoding: utf-8
import time
import datetime

from django.db import models

from juntagrico.dao.sharedao import ShareDao
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao

from juntagrico.mailer import *
from juntagrico.util.temporal import *
from juntagrico.util.bills import *
from juntagrico.config import Config

from juntagrico.entity.billing import *
from juntagrico.entity.subtypes import *


class Subscription(Billable):
    '''
    One Subscription that may be shared among several people.
    '''
    depot = models.ForeignKey('Depot', on_delete=models.PROTECT, related_name='subscription_set')
    future_depot = models.ForeignKey('Depot', on_delete=models.PROTECT, related_name='future_subscription_set', null=True,
                                     blank=True, )
    types = models.ManyToManyField('SubscriptionType',through='TSST', related_name='subscription_set')
    future_types = models.ManyToManyField('SubscriptionType',through='TFSST', related_name='future_subscription_set')
    primary_member = models.ForeignKey('Member', related_name='subscription_primary', null=True, blank=True,
                                       on_delete=models.PROTECT)
    active = models.BooleanField(default=False)
    canceled = models.BooleanField('gekündigt', default=False)
    activation_date = models.DateField('Aktivierungssdatum', null=True, blank=True)
    deactivation_date = models.DateField('Deaktivierungssdatum', null=True, blank=True)
    cancelation_date = models.DateField('Kündigüngssdatum', null=True, blank=True)
    creation_date = models.DateField('Erstellungsdatum', null=True, blank=True, auto_now_add=True)
    start_date = models.DateField('Gewünschtes Startdatum', null=False, default=start_of_next_business_year)
    end_date = models.DateField('Gewünschtes Enddatum', null=True,blank=True)
    notes = models.TextField('Notizen', max_length=1000, blank=True)    
    old_active = None
    old_canceled = None

    def __str__(self):
        namelist = ['1 Einheit' if self.size == 1 else '%d Einheiten' % self.size]
        namelist.extend(extra.type.name for extra in self.extra_subscriptions.all())
        return 'Abo (%s) %s' % (' + '.join(namelist), self.id)

    @property
    def overview(self):
        namelist = ['1 Einheit' if self.size == 1 else '%d Einheiten' % self.size]
        namelist.extend(extra.type.name for extra in self.extra_subscriptions.all())
        return '%s' % (' + '.join(namelist))
       
    @property   
    def size(self):
        result=0
        for type in self.types.all():
            result += type.size.size
        return result
    
    @property
    def types_changed(self):
        return set(self.types.all())!=set(self.future_types.all())

    def recipients_names(self):
        members = self.members.all()
        return ', '.join(str(member) for member in members)

    def other_recipients_names(self):
        members = self.recipients().exclude(email=self.primary_member.email)
        return ', '.join(str(member) for member in members)

    def recipients(self):
        return self.members.all()

    def primary_member_nullsave(self):
        member = self.primary_member
        return str(member) if member is not None else ''

    @property
    def state(self):
        if self.active is False and self.deactivation_date is None:
            return 'waiting'
        elif self.active is True and self.canceled is False:
            return 'active'
        elif self.active is True and self.canceled is True:
            return 'canceled'
        elif self.active is False and self.deactivation_date is not None:
            return 'inactive'

    @property
    def extra_subscriptions(self):
        return self.extra_subscription_set.filter(active=True)

    @property
    def paid_shares(self):
        return ShareDao.paid_shares(self).count()

    @property
    def all_shares(self):
        return ShareDao.all_shares_subscription(self).count()

    @property
    def future_extra_subscriptions(self):
        return self.extra_subscription_set.filter(
            Q(active=False, deactivation_date=None) | Q(active=True, canceled=False))
            
    @property
    def extrasubscriptions_changed(self):
        current_extrasubscriptions = self.extra_subscriptions.all()
        future_extrasubscriptions = self.future_extra_subscriptions.all()
        return set(current_extrasubscriptions) != set(future_extrasubscriptions)

    
    def subscription_amount(self, size_name):
        return self.calc_subscritpion_amount(self.types, size_name)

    def subscription_amount_future(self, size_name):
        return self.calc_subscritpion_amount(self.future_types, size_name)

    @staticmethod
    def calc_subscritpion_amount(types, size_name):
        result = 0
        for type in types.all():
            if type.size.name == size_name:
                result += 1
        return result
        

    @staticmethod
    def next_extra_change_date():
        month = int(time.strftime('%m'))
        if month >= 7:
            next_extra = datetime.date(day=1, month=1, year=timezone.now().today().year + 1)
        else:
            next_extra = datetime.date(day=1, month=7, year=timezone.now().today().year)
        return next_extra
        
    @staticmethod
    def next_size_change_date():
        return start_of_next_business_year()

    @staticmethod
    def get_size_name(types=[]):
        size_names = []
        for type in types.all():
            size_names.append(type.__str__())
        if len(size_names) > 0:
            return ', '.join(size_names)
        return 'kein Abo'
        
    def required_assignments(self):
        result = 0
        for type in self.types.all():
            result += type.required_assignments
        return result
       
    @property
    def price(self):
        result = 0
        for type in self.types.all():
            result += type.price
        return result

    @property
    def size_name(self):
        return Subscription.get_size_name(types=self.types)

    @property
    def future_size_name(self):
        return Subscription.get_size_name(types=self.future_types)

    def extra_subscription(self, code):
        return len(self.extra_subscriptions.all().filter(type__name=code)) > 0

    def clean(self):
        if self.old_active != self.active and self.deactivation_date is not None:
            raise ValidationError('Deaktivierte Abos koennen nicht wieder aktiviert werden', code='invalid')

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        if instance.old_active != instance.active and instance.old_active is False and instance.deactivation_date is None:
            instance.activation_date = timezone.now().date()
            if Config.billing():
                bill_subscription(instance)
        elif instance.old_active != instance.active and instance.old_active is True and instance.deactivation_date is None:
            instance.deactivation_date = timezone.now().date()
        if instance.old_canceled != instance.canceled:
            send_subscription_canceled(instance)
            instance.cancelation_date = timezone.now().date()

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_active = instance.active
        instance.old_canceled = instance.canceled

    @classmethod
    def pre_delete(cls, sender, instance, **kwds):
        for member in instance.recipients():
            member.subscription = None
            member.save()

    class Meta:
        verbose_name = 'Abo'
        verbose_name_plural = 'Abos'
        permissions = (('can_filter_subscriptions', 'Benutzer kann Abos filtern'),)