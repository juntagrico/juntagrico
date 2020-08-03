import datetime
import time

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.dao.sharedao import ShareDao
from juntagrico.entity import notifiable, JuntagricoBaseModel, SimpleStateModel
from juntagrico.entity.billing import Billable
from juntagrico.entity.depot import Depot
from juntagrico.lifecycle.sub import check_sub_consistency
from juntagrico.util.models import q_activated, q_cancelled, q_deactivated
from juntagrico.util.temporal import start_of_next_business_year


class Subscription(Billable, SimpleStateModel):
    '''
    One Subscription that may be shared among several people.
    '''
    depot = models.ForeignKey(
        'Depot', on_delete=models.PROTECT, related_name='subscription_set')
    future_depot = models.ForeignKey(
        Depot, on_delete=models.PROTECT, related_name='future_subscription_set', null=True, blank=True,
        verbose_name=_('Zukünftiges {}').format(Config.vocabulary('depot')),
        help_text='Nur setzen, wenn {} geändert werden soll'.format(Config.vocabulary('depot')))
    primary_member = models.ForeignKey('Member', related_name='subscription_primary', null=True, blank=True,
                                       on_delete=models.PROTECT,
                                       verbose_name=_('Haupt-{}-BezieherIn').format(Config.vocabulary('subscription')))
    start_date = models.DateField(
        _('Gewünschtes Startdatum'), null=False, default=start_of_next_business_year)
    end_date = models.DateField(
        _('Gewünschtes Enddatum'), null=True, blank=True)
    notes = models.TextField(
        _('Notizen'), max_length=1000, blank=True,
        help_text=_('Notizen für Administration. Nicht sichtbar für {}'.format(Config.vocabulary('member'))))
    _future_members = None

    def __str__(self):
        return _('Abo ({1}) {0}').format(self.overview, self.id)

    @property
    def overview(self):
        namelist = [_(' Einheiten {0}').format(self.size)]
        namelist.extend(
            extra.type.name for extra in self.extra_subscriptions.all())
        return '%s' % (' + '.join(namelist))

    @staticmethod
    def get_size_name(parts):
        size_dict = {}
        for part in parts.all():
            size_dict[str(part.type)] = 1 + size_dict.get(str(part.type), 0)
        size_names = [key + ':' + str(value) for key, value in size_dict.items()]
        if len(size_names) > 0:
            return '<br>'.join(size_names)
        return _('keine {0}-Bestandteile').format(Config.vocabulary('subscription'))

    @property
    def size_name(self):
        return Subscription.get_size_name(self.active_parts)

    @property
    def future_size_name(self):
        return Subscription.get_size_name(self.future_parts)

    @property
    def active_parts(self):
        return self.parts.filter(q_activated & ~q_deactivated)

    @property
    def future_parts(self):
        return self.parts.filter(~q_cancelled & ~q_deactivated)

    @property
    def active_and_future_parts(self):
        return self.parts.filter(~q_deactivated)

    @property
    def part_change_date(self):
        order_dates = list(self.future_parts.values_list('creation_date', flat=True).order_by('creation_date'))
        cancel_dates = list(self.active_parts.values_list('cancellation_date', flat=True).order_by('cancellation_date'))
        dates = order_dates + cancel_dates
        return max([date for date in dates if date is not None])

    @property
    def size(self):
        sizes = {}
        for part in self.active_parts.all():
            sizes[part.type.size.product.name] = part.type.size.units + sizes.get(part.type.size.product.name, 0)
        return ', '.join([key + ':' + str(value) for key, value in sizes.items()])

    @property
    def types_changed(self):
        return self.parts.filter(~q_activated | (q_cancelled & ~q_deactivated)).count()

    @staticmethod
    def calc_subscription_amount(parts, size):
        return parts.filter(type__size=size).count()

    def future_amount_by_type(self, type):
        return len(self.future_parts.filter(type__id=type))

    def subscription_amount(self, size):
        return self.calc_subscription_amount(self.active_parts, size)

    def subscription_amount_future(self, size):
        return self.calc_subscription_amount(self.future_parts, size)

    @property
    def required_assignments(self):
        result = 0
        for part in self.active_parts.all():
            result += part.type.required_assignments
        return result

    @property
    def required_core_assignments(self):
        result = 0
        for part in self.active_parts.all():
            result += part.type.required_core_assignments
        return result

    @property
    def price(self):
        result = 0
        for part in self.active_parts.all():
            result += part.type.price
        return result

    @property
    def all_shares(self):
        return ShareDao.all_shares_subscription(self).count()

    @property
    def paid_shares(self):
        return ShareDao.paid_shares(self).count()

    @property
    def share_overflow(self):
        return self.all_shares - self.required_shares

    @property
    def required_shares(self):
        result = 0
        for part in self.future_parts.all():
            result += part.type.shares
        return result

    def recipients_names(self):
        members = self.recipients
        return ', '.join(str(member) for member in members)

    recipients_names.short_description = '{}-BezieherInnen'.format(Config.vocabulary('subscription'))

    def other_recipients(self):
        return self.recipients.exclude(email=self.primary_member.email)

    def other_recipients_names(self):
        members = self.other_recipients()
        return ', '.join(str(member) for member in members)

    @property
    def recipients(self):
        return self.subscriptionmembership_set.filter(leave_date__isnull=True)

    @property
    def recipients_all(self):
        return self.subscriptionmembership_set.filter(leave_date__isnull=True)

    def primary_member_nullsave(self):
        member = self.primary_member
        return str(member) if member is not None else ''

    primary_member_nullsave.short_description = primary_member.verbose_name

    @property
    def extra_subscriptions(self):
        return self.extra_subscription_set.filter(q_activated & ~q_deactivated)

    @property
    def future_extra_subscriptions(self):
        return self.extra_subscription_set.filter(~q_cancelled & ~q_deactivated)

    @property
    def extrasubscriptions_changed(self):
        current_extrasubscriptions = self.extra_subscriptions.all()
        future_extrasubscriptions = self.future_extra_subscriptions.all()
        return set(current_extrasubscriptions) != set(future_extrasubscriptions)

    def extra_subscription_amount(self, extra_sub_type):
        return self.extra_subscriptions.filter(type=extra_sub_type).count()

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

    def clean(self):
        check_sub_consistency(self)

    @notifiable
    class Meta:
        verbose_name = Config.vocabulary('subscription')
        verbose_name_plural = Config.vocabulary('subscription_pl')
        permissions = (('can_filter_subscriptions', _('Benutzer kann {0} filtern').format(Config.vocabulary('subscription'))),)


class SubscriptionPart(JuntagricoBaseModel, SimpleStateModel):
    subscription = models.ForeignKey('Subscription', related_name='parts', on_delete=models.CASCADE,
                                     verbose_name=Config.vocabulary('subscription'))
    type = models.ForeignKey('SubscriptionType', related_name='subscription_parts', on_delete=models.PROTECT,
                             verbose_name=_('{0}-Typ').format(Config.vocabulary('subscription')))

    @property
    def can_cancel(self):
        # TODO
        return True

    class Meta:
        verbose_name = _('{} Bestandteil').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{} Bestandteile').format(Config.vocabulary('subscription'))
