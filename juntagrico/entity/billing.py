from django.db import models
from django.utils.translation import gettext as _

from juntagrico.entity import JuntagricoBasePoly, JuntagricoBaseModel
from juntagrico.util.temporal import month_choices


class Billable(JuntagricoBasePoly):
    '''
    Parent type for billables.
    '''

    class Meta:
        verbose_name = _('Verrechenbare Einheit')
        verbose_name_plural = _('Verrechenbare Einheiten')


class ExtraSubBillingPeriod(JuntagricoBaseModel):
    '''
    Billing Period for Extra subscriptions for which a bill has to be issued
    '''

    type = models.ForeignKey('ExtraSubscriptionType', related_name='periods', null=False, blank=False,
                             on_delete=models.PROTECT)
    price = models.DecimalField(_('Preis'), max_digits=10, decimal_places=2)
    start_day = models.PositiveIntegerField(_('Start Tag'))
    start_month = models.PositiveIntegerField(
        _('Start Monat'), choices=month_choices)
    end_day = models.PositiveIntegerField(_('End Tag'))
    end_month = models.PositiveIntegerField(
        _('End Monat'), choices=month_choices)
    cancel_day = models.PositiveIntegerField(_('Kündigungs Tag'))
    cancel_month = models.PositiveIntegerField(
        _('Kündigungs Monat'), choices=month_choices)
    code = models.TextField(_('Code für Teilabrechnung'),
                            max_length=1000, default='', blank=True)

    def __str__(self):
        return '{0}({1}.{2} - {3}.{4})'.format(self.type.name,
                                               self.start_day,
                                               self.start_month,
                                               self.end_day,
                                               self.end_month)

    class Meta:
        verbose_name = _('Verechnungsperdiode Zusatzabos')
        verbose_name_plural = _('Verechnungsperdioden Zusatzabos')
