from datetime import datetime, timedelta, time
from django.template.defaultfilters import date

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel
from juntagrico.util.models import q_isactive
from juntagrico.util.temporal import weekday_choices


class Depot(JuntagricoBaseModel):
    '''
    Location where stuff is picked up.
    '''
    name = models.CharField(_('{0} Name').format(Config.vocabulary('depot')), max_length=100, unique=True)
    contact = models.ForeignKey('Member', on_delete=models.PROTECT)
    weekday = models.PositiveIntegerField(_('Wochentag'), choices=weekday_choices)
    pickup_time = models.TimeField(_('Abholzeit'), null=True, blank=True)
    pickup_duration = models.FloatField(_('Abholzeitfenster in Stunden'), null=True, blank=True,
                                        validators=[MinValueValidator(0)])
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
    access_information = models.TextField(_('Zugangsbeschreibung'), max_length=1000, default='',
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
    def has_geo(self):
        lat = self.latitude is not None and self.latitude != ''
        long = self.longitude is not None and self.longitude != ''
        street = self.addr_street is not None and self.addr_street != ''
        zip = self.addr_zipcode is not None and self.addr_zipcode != ''
        loc = self.addr_location is not None and self.addr_location != ''
        return lat and long and street and zip and loc

    @property
    def pickup_end_time(self):
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
            end_time = self.pickup_end_time
            display_format = []
            if end_time.time() > time.min:
                display_format.append('H:i')
            else:
                # if end_time is midnight, show the previous day as end day
                end_time -= timedelta(1)
            if end_time.isoweekday() != self.weekday:
                display_format.insert(0, 'l')
            if display_format:
                parts.append(_('bis'))
                parts.append(date(end_time, ' '.join(display_format)))
        return ' '.join(parts)

    class Meta:
        verbose_name = Config.vocabulary('depot')
        verbose_name_plural = Config.vocabulary('depot_pl')
        ordering = ['sort_order']
        permissions = (('is_depot_admin', _('Benutzer ist Depot Admin')),)
