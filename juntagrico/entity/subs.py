# encoding: utf-8
import time
import datetime

from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

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
    depot = models.ForeignKey(
        'Depot', on_delete=models.PROTECT, related_name='subscription_set')
    future_depot = models.ForeignKey('Depot', on_delete=models.PROTECT, related_name='future_subscription_set', null=True,
                                     blank=True, )
    types = models.ManyToManyField(
        'SubscriptionType', through='TSST', related_name='subscription_set')
    future_types = models.ManyToManyField(
        'SubscriptionType', through='TFSST', related_name='future_subscription_set')
    primary_member = models.ForeignKey('Member', related_name='subscription_primary', null=True, blank=True,
                                       on_delete=models.PROTECT)
    active = models.BooleanField(default=False)
    canceled = models.BooleanField(_('gekündigt'), default=False)
    activation_date = models.DateField(
        _('Aktivierungssdatum'), null=True, blank=True)
    deactivation_date = models.DateField(
        _('Deaktivierungssdatum'), null=True, blank=True)
    cancelation_date = models.DateField(
        _('Kündigüngssdatum'), null=True, blank=True)
    creation_date = models.DateField(
        _('Erstellungsdatum'), null=True, blank=True, auto_now_add=True)
    start_date = models.DateField(
        _('Gewünschtes Startdatum'), null=False, default=start_of_next_business_year)
    end_date = models.DateField(
        _('Gewünschtes Enddatum'), null=True, blank=True)
    notes = models.TextField(_('Notizen'), max_length=1000, blank=True)
    old_active = None
    old_canceled = None

    def __str__(self):
        namelist = [_('1 Einheit') if self.size == 1 else _(
            '%(amount)d Einheiten') % {'amount': self.size}]
        namelist.extend(
            extra.type.name for extra in self.extra_subscriptions.all())
        return _('Abo (%(namelist)s) %(id)s') % {'namelist': ' + '.join(namelist), 'id': self.id}

    @property
    def overview(self):
        namelist = [_('1 Einheit') if self.size == 1 else _(
            '%(amount)s Einheiten') % {'amount': self.size}]
        namelist.extend(
            extra.type.name for extra in self.extra_subscriptions.all())
        return '%s' % (' + '.join(namelist))

    @property
    def size(self):
        result = 0
        for type in self.types.all():
            result += type.size.units
        return result

    @property
    def types_changed(self):
        return sorted(list(self.types.all())) != sorted(list(self.future_types.all()))

    def recipients_names(self):
        members = self.recipients
        return ', '.join(str(member) for member in members)

    def other_recipients_names(self):
        members = self.recipients.exclude(email=self.primary_member.email)
        return ', '.join(str(member) for member in members)

    @property
    def recipients(self):
        return self.recipients_all.filter(inactive=False)

    @property
    def recipients_all(self):
        return self.recipients_all_for_state(self.state)

    def recipients_all_for_state(self, state):
        if state == 'waiting':
            return self.members_future.all()
        elif state == 'inactive':
            return self.members_old.all()
        else:
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
    def share_overflow(self):
        return self.all_shares - self.required_shares

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
            next_extra = datetime.date(
                day=1, month=1, year=timezone.now().today().year + 1)
        else:
            next_extra = datetime.date(
                day=1, month=7, year=timezone.now().today().year)
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

    @property
    def required_shares(self):
        result = 0
        for type in self.types.all():
            result += type.shares
        return result

    @property
    def required_assignments(self):
        result = 0
        for type in self.types.all():
            result += type.required_assignments
        return result

    @property
    def required_core_assignments(self):
        result = 0
        for type in self.types.all():
            result += type.required_core_assignments
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
        return self.extra_subscription_amount(code) > 0

    def extra_subscription_amount(self, code):
        return len(self.extra_subscriptions.all().filter(type__name=code))

    def clean(self):
        if self.old_active != self.active and self.deactivation_date is not None:
            raise ValidationError('Deaktivierte ' + Config.vocabulary(
                'subscription_pl') + ' koennen nicht wieder aktiviert werden', code='invalid')

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        if instance.old_active != instance.active and instance.old_active is False and instance.deactivation_date is None:
            instance.activation_date = instance.activation_date if instance.activation_date is not None else timezone.now().date()
            for member in instance.recipients_all_for_state('waiting'):
                if member.subscription is not None:
                    raise ValidationError('Ein Bezüger hat noch ein aktives ' +
                                          Config.vocabulary('subscription') + '!', code='invalid')
            for member in instance.recipients_all_for_state('waiting'):
                member.subscription = instance
                member.future_subscription = None
                member.save()
            if Config.billing():
                bill_subscription(instance)
        elif instance.old_active != instance.active and instance.old_active is True and instance.deactivation_date is None:
            instance.deactivation_date = instance.deactivation_date if instance.deactivation_date is not None else timezone.now().date()
            for member in instance.recipients_all_for_state('active'):
                member.old_subscriptions.add(instance)
                member.subscription = None
                member.save()
        if instance.old_canceled != instance.canceled:
            instance.cancelation_date = timezone.now().date()

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_active = instance.active
        instance.old_canceled = instance.canceled

    class Meta:
        verbose_name = Config.vocabulary('subscription')
        verbose_name_plural = Config.vocabulary('subscription_pl')
        permissions = (('can_filter_subscriptions', 'Benutzer kann ' +
                        Config.vocabulary('subscription') + ' filtern'),)
