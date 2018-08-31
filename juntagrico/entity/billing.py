# encoding: utf-8

from django.db import models
from polymorphic.models import PolymorphicModel
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.util.temporal import month_choices, calculate_last
from juntagrico.util.temporal import calculate_next, calculate_next_offset


class Billable(PolymorphicModel):
    '''
    Parent type for billables.
    '''

    class Meta:
        verbose_name = _('Verrechenbare Einheit')
        verbose_name_plural = _('Verrechenbare Einheiten')


class Bill(models.Model):
    '''
    Actuall Bill for billables
    '''
    billable = models.ForeignKey('Billable', related_name='bills',
                                 null=False, blank=False,
                                 on_delete=models.PROTECT)
    paid = models.BooleanField(_('bezahlt'), default=False)
    bill_date = models.DateField(
        _('Aktivierungssdatum'), null=True, blank=True)
    ref_number = models.CharField(
        _('Referenznummer'), max_length=30, unique=True)
    amount = models.FloatField(_('Betrag'), null=False, blank=False)

    def __str__(self):
        return '%s' % self.ref_number

    class Meta:
        verbose_name = _('Rechnung')
        verbose_name_plural = _('Rechnungen')


class Payment(models.Model):
    '''
    Payment for bill
    '''
    bill = models.ForeignKey('Bill', related_name='payments',
                             null=False, blank=False,
                             on_delete=models.PROTECT)
    paid_date = models.DateField(_('Bezahldatum'), null=True, blank=True)
    amount = models.FloatField(_('Betrag'), null=False, blank=False)

    def __str__(self):
        return '%s' % self.ref_number

    class Meta:
        verbose_name = _('Zahlung')
        verbose_name_plural = _('Zahlungen')


class ExtraSubBillingPeriod(models.Model):
    '''
    Billing Period for Extra subscriptions for which a bill has to be issued
    '''

    type = models.ForeignKey('ExtraSubscriptionType', related_name='periods', null=False, blank=False,
                             on_delete=models.PROTECT)
    price = models.DecimalField('Preis', max_digits=10, decimal_places=2)
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

    def partial_price(self):
        now = timezone.now()
        start = calculate_last(self.start_day, self.start_month)
        end = calculate_next(self.end_day, self.end_month)
        return self.calc_price(start, end, now)

    def calculated_price(self, activation_date):
        start = calculate_last(self.start_day, self.start_month)
        end = calculate_next(self.end_day, self.end_month)
        ref_date = max(activation_date, start)
        return self.calc_price(start, end, ref_date=ref_date)

    def calc_price(self, start, end, now=None, ref_date=None):
        if self.code != '':
            exec(self.code)
        else:
            total_days = (end - start).days
            c_start = ref_date or start
            c_end = now or end
            passed_days = (c_end - c_start).days
            price = self.price * (passed_days/total_days)
        return price

    def get_actual_start(self, activation_date=None):
        start = calculate_last(self.start_day, self.start_month)
        if activation_date is None:
            return start
        return max(activation_date, start)

    def get_actual_end(self):
        return calculate_next(self.end_day, self.end_month)

    def get_actual_cancel(self):
        return calculate_next_offset(self.cancel_day,
                                     self.cancel_month,
                                     self.get_actual_start())

    def __str__(self):
        return '{0}({1}.{2} - {3}.{4})'.format(self.type.name,
                                               self.start_day,
                                               self.start_month,
                                               self.end_day,
                                               self.end_month)

    class Meta:
        verbose_name = _('Verechnungsperdiode Zusatzabos')
        verbose_name_plural = _('Verechnungsperdioden Zusatzabos')
