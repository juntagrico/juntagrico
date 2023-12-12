import datetime

from django.contrib import admin
from django.db import models
from django.db.models import Q, F, Sum
from django.utils.translation import gettext as _
from polymorphic.managers import PolymorphicManager

from juntagrico.config import Config
from juntagrico.dao.sharedao import ShareDao
from juntagrico.entity import notifiable, JuntagricoBaseModel, SimpleStateModel
from juntagrico.entity.billing import Billable
from juntagrico.entity.depot import Depot
from juntagrico.entity.member import q_left_subscription, q_joined_subscription
from juntagrico.entity.subtypes import SubscriptionType
from juntagrico.lifecycle.sub import check_sub_consistency
from juntagrico.lifecycle.subpart import check_sub_part_consistency
from juntagrico.queryset.subscription import SubscriptionQuerySet, SubscriptionPartQuerySet
from juntagrico.mailer import membernotification
from juntagrico.util.models import q_activated, q_cancelled, q_deactivated, q_deactivation_planned, q_isactive
from juntagrico.util.temporal import start_of_next_business_year


class Subscription(Billable, SimpleStateModel):
    '''
    One Subscription that may be shared among several people.
    '''
    depot = models.ForeignKey(
        Depot, on_delete=models.PROTECT, related_name='subscription_set')
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
        _('Notizen'), blank=True,
        help_text=_('Notizen für Administration. Nicht sichtbar für {}'.format(Config.vocabulary('member'))))

    objects = PolymorphicManager.from_queryset(SubscriptionQuerySet)()

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
    def size(self):
        delimiter = Config.sub_overview_format('delimiter')
        sformat = Config.sub_overview_format('format')
        types = SubscriptionType.objects.filter(subscription_parts__in=self.active_and_future_parts).annotate(
            size_sum=Sum('size__units'),
            size_name=F('size__name'),
            product_name=F('size__product__name')
        )
        return delimiter.join(
            [sformat.format(
                product=t.product_name,
                size=t.size_name,
                type=t.name,
                amount=t.size_sum,
            ) for t in types]
        )

    @property
    def types_changed(self):
        return self.parts.filter(~q_activated() | (q_cancelled() & ~q_deactivation_planned())).filter(type__size__product__is_extra=False).count()

    @staticmethod
    def calc_subscription_amount(parts, size):
        return parts.filter(type__size=size).count()

    def subscription_amount(self, size):
        return self.calc_subscription_amount(self.active_parts, size)

    def subscription_amount_future(self, size):
        return self.calc_subscription_amount(self.future_parts, size)

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
        member_active = ~Q(member__deactivation_date__isnull=False,
                           member__deactivation_date__lte=datetime.date.today())
        if self.waiting:
            return self.subscriptionmembership_set.prefetch_related('member').filter(member_active)
        elif self.inactive:
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

    def activate_future_depot(self):
        if self.future_depot is not None:
            self.depot = self.future_depot
            self.future_depot = None
            self.save()
            emails = []
            for member in self.recipients:
                emails.append(member.email)
            membernotification.depot_changed(emails, self.depot)

    def clean(self):
        check_sub_consistency(self)

    @notifiable
    class Meta:
        verbose_name = Config.vocabulary('subscription')
        verbose_name_plural = Config.vocabulary('subscription_pl')
        permissions = (
            ('can_filter_subscriptions', _('Benutzer kann {0} filtern').format(Config.vocabulary('subscription'))),
            ('can_change_deactivated_subscriptions', _('Benutzer kann deaktivierte {0} ändern').format(Config.vocabulary('subscription'))),
            ('notified_on_depot_change', _('Wird bei {0}-Änderung informiert').format(Config.vocabulary('depot'))),
        )


class SubscriptionPart(JuntagricoBaseModel, SimpleStateModel):
    subscription = models.ForeignKey('Subscription', related_name='parts', on_delete=models.CASCADE,
                                     verbose_name=Config.vocabulary('subscription'))
    type = models.ForeignKey('SubscriptionType', related_name='subscription_parts', on_delete=models.PROTECT,
                             verbose_name=_('{0}-Typ').format(Config.vocabulary('subscription')))

    objects = SubscriptionPartQuerySet.as_manager()

    def __str__(self):
        try:
            return Config.sub_overview_format('part_format').format(
                product=self.type.size.product.name,
                size=self.type.size.name,
                size_long=self.type.size.long_name,
                type=self.type.name,
                type_long=self.type.long_name,
                price=self.type.price
            )
        except KeyError as k:
            return _(f'Fehler in der Einstellung SUB_OVERVIEW_FORMAT.part_format. {k} kann nicht aufgelöst werden.')

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
