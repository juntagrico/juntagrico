# encoding: utf-8

from django.db import models

class SubscriptionSize(models.Model):
    '''
    Subscription sizes
    '''
    name = models.CharField('Name', max_length=100, unique=True)
    long_name = models.CharField('Langer Name', max_length=100, unique=True)
    size = models.PositiveIntegerField('Grösse', unique=True)
    depot_list = models.BooleanField('Sichtbar auf Depotliste', default=True)
    description = models.TextField('Beschreibung', max_length=1000, blank=True)    

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Abo Grösse'
        verbose_name_plural = 'Abo Grössen'
        

class SubscriptionType(models.Model):
    '''
    Subscription types
    '''
    name = models.CharField('Name', max_length=100)
    long_name = models.CharField('Langer Name', max_length=100, blank=True)
    size = models.ForeignKey('SubscriptionSize', on_delete=models.PROTECT, related_name='types')
    shares = models.PositiveIntegerField('Anz benötigter Anteilsscheine')
    required_assignments = models.PositiveIntegerField('Anz benötigter Arbeitseinsätze')
    price = models.PositiveIntegerField('Preis')
    visible = models.BooleanField('Sichtbar', default=True)
    description = models.TextField('Beschreibung', max_length=1000, blank=True)    

    def __str__(self):
        return self.name + ' - Grösse: ' + self.size.name

    class Meta:
        verbose_name = 'Abo Typ'
        verbose_name_plural = 'Abo Typen'
        
'''
through classes
'''

class TSST(models.Model):
    '''
    through class for subscription and subscription types
    '''
    subscription = models.ForeignKey('Subscription', related_name='STSST')
    type = models.ForeignKey('SubscriptionType', related_name='TTSST')

class TFSST(models.Model):
    '''
    through class for future subscription and subscription types
    '''
    subscription = models.ForeignKey('Subscription', related_name='STFSST')
    type = models.ForeignKey('SubscriptionType', related_name='TTFSST')