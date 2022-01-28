from django.db import models
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel, absolute_url
from juntagrico.entity.location import Location
from juntagrico.util.models import q_isactive
from juntagrico.util.temporal import weekday_choices, weekdays


@absolute_url(name='depot')
class Depot(JuntagricoBaseModel):
    '''
    Location where stuff is picked up.
    '''
    name = models.CharField(_('{0} Name').format(Config.vocabulary('depot')), max_length=100, unique=True)
    contact = models.ForeignKey('Member', on_delete=models.PROTECT)
    weekday = models.PositiveIntegerField(_('Wochentag'), choices=weekday_choices)
    capacity = models.PositiveIntegerField(_('Kapazität'), default=0)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, verbose_name=_('Ort'))
    description = models.TextField(_('Beschreibung'), max_length=1000, default='', blank=True)
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
    def map_info(self):
        map_info = self.location.map_info
        map_info['name'] = self.name
        return map_info

    @property
    def weekday_name(self):
        day = _('Unbekannt')
        if 8 > self.weekday > 0:
            day = weekdays[self.weekday]
        return day

    class Meta:
        verbose_name = Config.vocabulary('depot')
        verbose_name_plural = Config.vocabulary('depot_pl')
        ordering = ['sort_order']
        permissions = (('is_depot_admin', _('Benutzer ist Depot Admin')),)
