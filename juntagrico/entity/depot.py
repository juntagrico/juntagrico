from datetime import datetime, timedelta, time

from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.db import models
from django.template.defaultfilters import date
from django.utils.translation import gettext, gettext_lazy as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel, absolute_url
from juntagrico.entity.contact import Contact, MemberContact, TextContact
from juntagrico.entity.location import Location
from juntagrico.queryset.depot import TourQueryset
from juntagrico.util.models import q_isactive
from juntagrico.util.temporal import weekday_choices


class Tour(JuntagricoBaseModel):
    """
    Delivery Tour to depots
    """
    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(_('Beschreibung'), default='', blank=True)
    weekday = models.PositiveIntegerField(_('Wochentag'), choices=weekday_choices, blank=True, null=True)
    visible_on_list = models.BooleanField(_('Sichtbar auf Listen'), default=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    objects = TourQueryset.as_manager()

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
    contact_set = GenericRelation(Contact)
    tour = models.ForeignKey(Tour, on_delete=models.PROTECT, related_name='depots',
                             verbose_name=_('Ausfahrt'), blank=True, null=True)
    weekday = models.PositiveIntegerField(_('Abholtag'), choices=weekday_choices)
    pickup_time = models.TimeField(_('Abholzeit'), null=True, blank=True)
    pickup_duration = models.FloatField(_('Abholzeitfenster in Stunden'), null=True, blank=True,
                                        validators=[MinValueValidator(0)])
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
    coordinators = models.ManyToManyField('Member', verbose_name=_('Koordinatoren'), through='DepotCoordinator',
                                          related_name='coordinated_depots')
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    overview_cache = None
    subscription_cache = None

    def __str__(self):
        return '%s %s' % (self.id, self.name)

    @property
    def contacts(self):
        if self.contact_set.count():
            return self.contact_set.all()
        # last resort: show depot coordinators as contact
        return [MemberContact(member=m) for m in self.coordinators.all()]

    def contact_names(self):
        for contact in self.contacts:
            if isinstance(contact, MemberContact):
                yield contact.member
            elif isinstance(contact, TextContact):
                yield contact.text

    def get_contact_options(self):
        return self.coordinators.all()

    def active_subscriptions(self):
        return self.subscription_set.filter(q_isactive()).order_by('primary_member__first_name',
                                                                   'primary_member__last_name')

    @property
    def map_info(self):
        map_info = self.location.map_info
        map_info['name'] = self.name
        map_info['id'] = self.id
        return map_info

    def total_fee(self, subscription_count):
        """
        :param subscription_count: a dict of subscription_type => amount or subscription_type_id => amount
        :return: total fee for this depot with selected subscription.
        """
        fee = self.fee
        # normalize count dict
        subscription_count = {
            int(k) if isinstance(k, (int, str)) else k.id: v for k, v in subscription_count.items() if v > 0
        }
        # get fees of relevant types and sum them
        conditions = self.subscription_type_conditions.filter(subscription_type__in=subscription_count.keys())
        for condition in conditions:
            fee += condition.fee * subscription_count[condition.subscription_type.id]
        return fee

    def pickup_end_time(self):
        # returns datetime with weekday and time of pickup. Rest of date is arbitrary
        start_date = datetime.strptime('1970 1 ' + str(self.weekday), '%Y %W %w')
        start_datetime = datetime.combine(start_date, self.pickup_time or time.min)
        return start_datetime + timedelta(hours=self.pickup_duration)

    @property
    def pickup_display(self):
        """ get string with pickup start day, end time, if it is not midnight
         end day if it is different than start day and end time if it is not midnight
        """
        parts = [self.get_weekday_display()]
        if self.pickup_time and self.pickup_time > time.min:
            parts.append(date(self.pickup_time, 'H:i'))
        if self.pickup_duration:
            end_time = self.pickup_end_time()
            display_format = []
            if end_time.time() > time.min:
                display_format.append('H:i')
            else:
                # if end_time is midnight, show the previous day as end day
                end_time -= timedelta(1)
            if end_time.isoweekday() != self.weekday:
                display_format.insert(0, 'l')
            if display_format:
                parts.append(gettext('bis'))
                parts.append(date(end_time, ' '.join(display_format)))
        return ' '.join(parts)

    class Meta:
        verbose_name = Config.vocabulary('depot')
        verbose_name_plural = Config.vocabulary('depot_pl')
        ordering = ['sort_order']


class DepotCoordinator(JuntagricoBaseModel):
    depot = models.ForeignKey(Depot, related_name='coordinator_access', on_delete=models.CASCADE)
    member = models.ForeignKey('Member', related_name='depot_access', on_delete=models.PROTECT)
    can_modify_depot = models.BooleanField(_('Kann Beschreibung ändern'), default=True)
    can_view_member = models.BooleanField(_('Kann {0} sehen').format(Config.vocabulary('member_pl')), default=True)
    can_contact_member = models.BooleanField(_('Kann {0} kontaktieren').format(Config.vocabulary('member_pl')), default=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    class Meta:
        verbose_name = _('Koordinator')
        verbose_name_plural = _('Koordinatoren')
        ordering = ['sort_order']
        constraints = [
            models.UniqueConstraint(fields=['depot', 'member'], name='unique_depot_member'),
        ]


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
