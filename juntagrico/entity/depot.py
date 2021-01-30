from django.core import validators
from django.db import models
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel
from juntagrico.util.models import q_isactive
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
        return self.subscription_set.filter(q_isactive()).order_by('primary_member__first_name', 'primary_member__last_name')

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

    class Meta:
        verbose_name = Config.vocabulary('depot')
        verbose_name_plural = Config.vocabulary('depot_pl')
        permissions = (('is_depot_admin', _('Benutzer ist Depot Admin')),)
