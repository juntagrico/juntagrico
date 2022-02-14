from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.dao.sharedao import ShareDao
from juntagrico.entity import notifiable, JuntagricoBaseModel, SimpleStateModel
from juntagrico.entity.billing import Billable
from juntagrico.entity.depot import Depot
from juntagrico.entity.member import q_left_subscription, q_joined_subscription
from juntagrico.lifecycle.sub import check_sub_consistency
from juntagrico.lifecycle.subpart import check_sub_part_consistency
from juntagrico.util.models import q_activated, q_cancelled, q_deactivated, q_deactivation_planned, q_isactive
from juntagrico.util.temporal import start_of_next_business_year, start_of_business_year, \
    calculate_remaining_days_percentage


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
    nickname = models.CharField(_('Spitzname'), max_length=30, blank=True,
                                help_text=_('Ersetzt die Mit-{}-BezieherInnen auf der {}-Liste.'.format(
                                    Config.vocabulary('subscription'), Config.vocabulary('depot'))))
    start_date = models.DateField(
        _('Gewünschtes Startdatum'), null=False, default=start_of_next_business_year)
    end_date = models.DateField(
        _('Gewünschtes Enddatum'), null=True, blank=True)
    notes = models.TextField(
        _('Notizen'), max_length=1000, blank=True,
        help_text=_('Notizen für Administration. Nicht sichtbar für {}'.format(Config.vocabulary('member'))))

    def __str__(self):
        return _('Abo ({1}) {0}').format(self.size, self.id)

    @staticmethod
    def get_part_overview(parts):
        # building multi-dimensional dictionary [product_name][size_long_name][(type_name, type_long_name)] -> amount
        result = {}
        for part in parts.all():
            product_name = part.type.size.product.name
            product = result.get(product_name, {})
            size_name = part.type.size.long_name
            size = product.get(size_name, {})
            type_name = (part.type.name, part.type.long_name)
            size[type_name] = 1 + size.get(type_name, 0)
            product[size_name] = size
            result[product_name] = product
        return result

    @property
    def part_overview(self):
        return Subscription.get_part_overview(self.active_parts)

    @property
    def future_part_overview(self):
        return Subscription.get_part_overview(self.future_parts)

    @property
    def active_parts(self):
        return self.parts.filter(q_isactive())

    @property
    def future_parts(self):
        return self.parts.filter(~q_cancelled() & ~q_deactivated())

    @property
    def active_and_future_parts(self):
        return self.parts.filter(~q_deactivated())

    @property
    def part_change_date(self):
        order_dates = list(self.future_parts.values_list('creation_date', flat=True).order_by('creation_date'))
        cancel_dates = list(self.active_parts.values_list('cancellation_date', flat=True).order_by('cancellation_date'))
        dates = order_dates + cancel_dates
        return max([date for date in dates if date is not None])

    @property
    def size(self):
        delimiter = Config.sub_overview_format('delimiter')
        sformat = Config.sub_overview_format('format')
        sizes = {}
        for part in self.active_parts.all() or self.future_parts.all():
            sizes[part.type] = part.type.size.units + sizes.get(part.type, 0)
        return delimiter.join(
            [sformat.format(
                product=key.size.product.name,
                size=key.size.name,
                type=key.name,
                amount=value,
            ) for key, value in sizes.items()]
        )

    @property
    def types_changed(self):
        return self.parts.filter(~q_activated() | (q_cancelled() & ~q_deactivation_planned())).filter(type__size__product__is_extra=False).count()

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
        if self.activation_date is not None and self.activation_date > start_of_business_year():
            result = round(result * calculate_remaining_days_percentage(self.activation_date))
        return result

    @property
    def required_core_assignments(self):
        result = 0
        for part in self.active_parts.all():
            result += part.type.required_core_assignments
        if self.activation_date is not None and self.activation_date > start_of_business_year():
            result = round(result * calculate_remaining_days_percentage(self.activation_date))
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

    @admin.display(description='{}-BezieherInnen'.format(Config.vocabulary('subscription')))
    def recipients_names(self):
        members = self.recipients
        return ', '.join(str(member) for member in members)

    def co_members(self, member):
        qs = self.recipients_qs
        if member is not None:
            qs = qs.exclude(member__email=member.email)
        return [m.member for m in qs.all()]

    def recipients_display_name(self):
        if self.nickname:
            return ', '.join([self.primary_member_nullsave(), self.nickname])
        else:
            return '{}, {}'.format(self.primary_member_nullsave(), self.other_recipients_names)

    def other_recipients(self):
        return self.co_members(self.primary_member)

    @property
    def other_recipients_names(self):
        members = self.other_recipients()
        return ', '.join(str(member) for member in members)

    @property
    def recipients_qs(self):
        return self.memberships_for_state.order_by(
            'member__first_name', 'member__last_name')

    @property
    def recipients(self):
        return [m.member for m in self.recipients_qs.all()]

    @property
    def recipients_all(self):
        return [m.member for m in self.memberships_for_state.all()]

    @property
    def future_members(self):
        if getattr(self, 'override_future_members', False):
            return self.override_future_members
        qs = self.subscriptionmembership_set.filter(~q_left_subscription()).prefetch_related('member')
        return set([m.member for m in qs])

    @property
    def memberships_for_state(self):
        now = timezone.now().date()
        member_active = ~Q(member__deactivation_date__isnull=False, member__deactivation_date__lte=now)
        if self.state == 'waiting':
            return self.subscriptionmembership_set.prefetch_related('member').filter(member_active)
        elif self.state == 'inactive':
            return self.subscriptionmembership_set.prefetch_related('member')
        else:
            return self.subscriptionmembership_set.filter(q_joined_subscription(),
                                                          ~q_left_subscription(), member_active).prefetch_related('member')

    @admin.display(description=primary_member.verbose_name)
    def primary_member_nullsave(self):
        member = self.primary_member
        return str(member) if member is not None else ''

    @property
    def extra_subscriptions(self):
        return self.active_parts.filter(type__size__product__is_extra=True)

    @property
    def future_extra_subscriptions(self):
        return self.future_parts.filter(type__size__product__is_extra=True)

    @property
    def active_and_future_extra_subscriptions(self):
        return self.active_and_future_parts.filter(type__size__product__is_extra=True)

    @property
    def extrasubscriptions_changed(self):
        return self.parts.filter(~q_activated() | (q_cancelled() & ~q_deactivation_planned())).filter(type__size__product__is_extra=True).count()

    def extra_subscription_amount(self, extra_sub_type):
        return self.extra_subscriptions.filter(type=extra_sub_type).count()

    @staticmethod
    def next_size_change_date():
        return start_of_next_business_year()

    def clean(self):
        check_sub_consistency(self)

    @notifiable
    class Meta:
        verbose_name = Config.vocabulary('subscription')
        verbose_name_plural = Config.vocabulary('subscription_pl')
        permissions = (
            ('can_filter_subscriptions', _('Benutzer kann {0} filtern').format(Config.vocabulary('subscription'))),
            ('can_change_deactivated_subscriptions', _('Benutzer kann deaktivierte {0} ändern').format(Config.vocabulary('subscription'))),)


class SubscriptionPart(JuntagricoBaseModel, SimpleStateModel):
    subscription = models.ForeignKey('Subscription', related_name='parts', on_delete=models.CASCADE,
                                     verbose_name=Config.vocabulary('subscription'))
    type = models.ForeignKey('SubscriptionType', related_name='subscription_parts', on_delete=models.PROTECT,
                             verbose_name=_('{0}-Typ').format(Config.vocabulary('subscription')))

    @property
    def can_cancel(self):
        return self.cancellation_date is None and self.subscription.future_parts.count() > 1

    @property
    def is_extra(self):
        return self.type.size.product.is_extra

    def clean(self):
        check_sub_part_consistency(self)

    @notifiable
    class Meta:
        verbose_name = _('{} Bestandteil').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{} Bestandteile').format(Config.vocabulary('subscription'))
