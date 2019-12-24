import datetime
import time

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.dao.sharedao import ShareDao
from juntagrico.entity import notifiable
from juntagrico.entity.billing import Billable
from juntagrico.entity.depot import Depot
from juntagrico.lifecycle.sub import check_sub_consistency
from juntagrico.util.temporal import start_of_next_business_year


class Subscription(Billable):
    '''
    One Subscription that may be shared among several people.
    '''
    depot = models.ForeignKey(
        'Depot', on_delete=models.PROTECT, related_name='subscription_set')
    future_depot = models.ForeignKey(Depot, on_delete=models.PROTECT, related_name='future_subscription_set', null=True,
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
    _future_members = None

    def __str__(self):
        namelist = [_(' Einheiten {0}').format(self.size)]
        namelist.extend(
            extra.type.name for extra in self.extra_subscriptions.all())
        return _('Abo ({0}) {0}').format(' + '.join(namelist), self.id)

    @property
    def overview(self):
        namelist = [_(' Einheiten {0}').format(self.size)]
        namelist.extend(
            extra.type.name for extra in self.extra_subscriptions.all())
        return '%s' % (' + '.join(namelist))

    @property
    def size(self):
        sizes = {}
        for type in self.types.all():
            sizes[type.size.product.name] = type.size.units + sizes.get(type.size.product.name, 0)
        return ', '.join([key + ':' + str(value) for key, value in sizes.items()])

    @property
    def types_changed(self):
        return sorted(list(self.types.all())) != sorted(list(self.future_types.all()))

    def recipients_names(self):
        members = self.recipients
        return ', '.join(str(member) for member in members)

    def other_recipients(self):
        return self.recipients.exclude(email=self.primary_member.email)

    def other_recipients_names(self):
        members = self.other_recipients()
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

    def subscription_amount(self, size_id):
        return self.calc_subscription_amount(self.types, size_id)

    def subscription_amount_future(self, size_id):
        return self.calc_subscription_amount(self.future_types, size_id)

    @staticmethod
    def calc_subscription_amount(types, size_id):
        result = 0
        for type in types.all():
            if type.size.id == size_id:
                result += 1
        return result

    def future_amount_by_type(self, type):
        return len(self.future_types.filter(id=type))

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
        size_dict = {}
        for type in types.all():
            size_dict[type.__str__()] = 1 + size_dict.get(type.__str__(), 0)
        size_names = [key + ':' + str(value) for key, value in size_dict.items()]
        if len(size_names) > 0:
            return '<br>'.join(size_names)
        return _('kein/e/n {0}').format(Config.vocabulary('subscription'))

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
        check_sub_consistency(self)

    @notifiable
    class Meta:
        verbose_name = Config.vocabulary('subscription')
        verbose_name_plural = Config.vocabulary('subscription_pl')
        permissions = (('can_filter_subscriptions', _('Benutzer kann {0} filtern').format(Config.vocabulary('subscription'))),)
