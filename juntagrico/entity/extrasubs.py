from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.dao.extrasubbillingperioddao import ExtraSubBillingPeriodDao
from juntagrico.entity import JuntagricoBaseModel, SimpleStateModel
from juntagrico.entity.billing import Billable
from juntagrico.lifecycle.extrasub import check_extra_sub_consistency


class ExtraSubscriptionCategory(JuntagricoBaseModel):
    '''
    Types of extra subscriptions, e.g. eggs, cheese, fruit
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(
        _('Beschreibung'), max_length=1000, blank=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)
    visible = models.BooleanField(_('Sichtbar'), default=True)
    depot_list = models.BooleanField(_('Sichtbar auf Depotliste'), default=True)

    def __str__(self):
        return '%s %s' % (self.id, self.name)

    @property
    def types_for_depot_list(self):
        return self.types.filter(depot_list=True) if self.depot_list else []

    class Meta:
        verbose_name = _('Zusatz-Abo-Kategorie')
        verbose_name_plural = _('Zusatz-Abo-Kategorien')
        ordering = ['sort_order']


