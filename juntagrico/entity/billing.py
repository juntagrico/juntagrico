# encoding: utf-8

from django.db import models
from polymorphic.models import PolymorphicModel
from juntagrico.util.temporal import *


class Billable(PolymorphicModel):
    '''
    Parent type for billables.
    '''

    class Meta:
        verbose_name = 'Verrechenbare Einheit'
        verbose_name_plural = 'Verrechenbare Einhaiten'


class Bill(models.Model):
    '''
    Actuall Bill for billables
    '''
    billable = models.ForeignKey('Billable', related_name='bills', null=False, blank=False,
                                 on_delete=models.PROTECT)
    paid = models.BooleanField('bezahlt', default=False)
    bill_date = models.DateField('Aktivierungssdatum', null=True, blank=True)
    ref_number = models.CharField('Referenznummer', max_length=30, unique=True)
    amount = models.FloatField('Betrag', null=False, blank=False)

    def __str__(self):
        return '%s' % self.ref_number

    class Meta:
        verbose_name = 'Rechnung'
        verbose_name_plural = 'Rechnungen'


class Payment(models.Model):
    '''
    Payment for bill
    '''
    bill = models.ForeignKey('Bill', related_name='payments', null=False, blank=False,
                             on_delete=models.PROTECT)
    paid_date = models.DateField('Bezahldatum', null=True, blank=True)
    amount = models.FloatField('Betrag', null=False, blank=False)

    def __str__(self):
        return '%s' % self.ref_number

    class Meta:
        verbose_name = 'Zahlung'
        verbose_name_plural = 'Zahlung'
		
class ExtraSubBillingPeriod(models.Model):
    '''
    Billing Period for Extra subscriptions for which a bill has to be issued
    '''
    type = models.ForeignKey('ExtraSubscriptionType', related_name='periods', null=False, blank=False,
                                 on_delete=models.PROTECT)
    price = models.PositiveIntegerField('Preis')
    start_day = models.PositiveIntegerField('Start Tag')
    start_month = models.PositiveIntegerField('Start Monat', choices=month_choices)
    end_day = models.PositiveIntegerField('End Tag')
    end_month = models.PositiveIntegerField('End Monat', choices=month_choices)
    cancel_day = models.PositiveIntegerField('Kündigungs Tag')
    cancel_month = models.PositiveIntegerField('Kündigungs Monat', choices=month_choices)
    code = models.TextField('Code für Teilabrechnung', max_length=1000, default='', blank=True)
	
    def partial_price(self):
        now = timezone.now()
        start = calculate_last(self.start_day, self.start_month)
        end = calculate_next(self.end_day, self.end_month)
        if code !='':
            exec(code)
        else:
            total_days = (end - start).days
            passed_days = (now - start).days
            price = self.price *(passed_days/total_days)
	
    def calculated_price(self, activation_date):
        start = calculate_last(self.start_day, self.start_month)
        end = calculate_next(self.end_day, self.end_month)
        ref_date = max(activation_date, start)
        if code !='':
            exec(code)
        else:
            total_days = (end - start).days
            passed_days = (end - ref_date).days
            price = self.price *(passed_days/total_days)
            
    def get_actual_start(self, activation_date=None):
        start = calculate_last(self.start_day, self.start_month)
        if activation_date is None:
            return start
        return max(activation_date, start)
    
    def get_actual_end(self):
        return calculate_next(self.end_day, self.end_month)
        
    def get_actual_cancel(self):
        return calculate_next_offset(self.cancel_day, self.cancel_month, self.get_actual_start())
            
    def __str__(self):
        return '{0}({1}.{2} - {3}.{4})'.format(self.type.name, self.start_day, self.start_month, self.end_day, self.end_month)

    class Meta:
        verbose_name = 'Verechnungsperdiode Zusatzabos'
        verbose_name_plural = 'Verechnungsperdioden Zusatzabos'
