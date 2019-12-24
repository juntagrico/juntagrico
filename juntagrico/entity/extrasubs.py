from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.dao.extrasubbillingperioddao import ExtraSubBillingPeriodDao
from juntagrico.entity import JuntagricoBaseModel
from juntagrico.entity.billing import Billable


class ExtraSubscriptionType(JuntagricoBaseModel):
    '''
    Types of extra subscriptions, e.g. eggs, cheese, fruit
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True)
    size = models.CharField(_('Groesse (gross,4, ...)'),
                            max_length=100, default='')
    description = models.TextField(_('Beschreibung'), max_length=1000)
    sort_order = models.FloatField(_('Groesse zum Sortieren'), default=1.0)
    visible = models.BooleanField(_('Sichtbar'), default=True)
    category = models.ForeignKey('ExtraSubscriptionCategory', related_name='category', null=True, blank=True,

                                 on_delete=models.PROTECT)

    def __str__(self):
        return '%s %s' % (self.id, self.name)

    class Meta:
        verbose_name = _('Zusatz-Abo-Typ')
        verbose_name_plural = _('Zusatz-Abo-Typen')


class ExtraSubscriptionCategory(JuntagricoBaseModel):
    '''
    Types of extra subscriptions, e.g. eggs, cheese, fruit
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True)
    description = models.TextField(
        _('Beschreibung'), max_length=1000, blank=True)
    sort_order = models.FloatField(_('Nummer zum Sortieren'), default=1.0)
    visible = models.BooleanField(_('Sichtbar'), default=True)

    def __str__(self):
        return '%s %s' % (self.id, self.name)

    class Meta:
        verbose_name = _('Zusatz-Abo-Kategorie')
        verbose_name_plural = _('Zusatz-Abo-Kategorien')


class ExtraSubscription(Billable):
    '''
    The actiual extra subscription
    '''
    main_subscription = models.ForeignKey('Subscription', related_name='extra_subscription_set',
                                          on_delete=models.PROTECT)
    active = models.BooleanField(default=False)
    canceled = models.BooleanField(_('gekündigt'), default=False)
    activation_date = models.DateField(_('Aktivierungssdatum'), null=True, blank=True)
    deactivation_date = models.DateField(_('Deaktivierungssdatum'), null=True, blank=True)
    type = models.ForeignKey(ExtraSubscriptionType, related_name='extra_subscriptions', null=False, blank=False,
                             on_delete=models.PROTECT)

    @property
    def can_cancel(self):
        period = ExtraSubBillingPeriodDao.get_current_period_per_type(
            self.type)
        if period is not None:
            return timezone.now() <= period.get_actual_cancel()
        return False

    @property
    def state(self):
        if self.active is False and self.deactivation_date is None:
            return _('wartend')
        elif self.active is True and self.canceled is False:
            return _('aktiv')
        elif self.active is True and self.canceled is True:
            return _('aktiv - gekündigt')
        elif self.active is False and self.deactivation_date is not None:
            return _('inaktiv-gekündigt')

    def __str__(self):
        return '%s %s' % (self.id, self.type.name)

    class Meta:
        verbose_name = _('Zusatz-Abo')
        verbose_name_plural = _('Zusatz-Abos')
