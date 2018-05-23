from django.db import models
from django.utils.translation import gettext as _

class SubscriptionSize(models.Model):
    '''
    Subscription sizes
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True)
    long_name = models.CharField(_('Langer Name'), max_length=100, unique=True)
    units = models.PositiveIntegerField(_('Einheiten'), unique=True)
    depot_list = models.BooleanField(_('Sichtbar auf Depotliste'), default=True)
    description = models.TextField(_('Beschreibung'), max_length=1000, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Abo Grösse')
        verbose_name_plural = _('Abo Grössen')
        

class SubscriptionType(models.Model):
    '''
    Subscription types
    '''
    name = models.CharField(_('Name'), max_length=100)
    long_name = models.CharField(_('Langer Name'), max_length=100, blank=True)
    size = models.ForeignKey('SubscriptionSize', on_delete=models.PROTECT, related_name='types')
    shares = models.PositiveIntegerField(_('Anz benötigter Anteilsscheine'))
    required_assignments = models.PositiveIntegerField(_('Anz benötigter Arbeitseinsätze'))
    price = models.PositiveIntegerField(_('Preis'))
    visible = models.BooleanField(_('Sichtbar'), default=True)
    description = models.TextField(_('Beschreibung'), max_length=1000, blank=True)

    def __str__(self):
        return self.name + _(' - Grösse: ') + self.size.name
    
    def __lt__(self, other):
        return self.pk < other.pk

    class Meta:
        verbose_name = _('Abo Typ')
        verbose_name_plural = _('Abo Typen')
        
'''
through classes
'''

class TSST(models.Model):
    '''
    through class for subscription and subscription types
    '''
    subscription = models.ForeignKey('Subscription', related_name='STSST', on_delete=models.CASCADE)
    type = models.ForeignKey('SubscriptionType', related_name='TTSST', on_delete=models.PROTECT)


class TFSST(models.Model):
    '''
    through class for future subscription and subscription types
    '''
    subscription = models.ForeignKey('Subscription', related_name='STFSST', on_delete=models.CASCADE)
    type = models.ForeignKey('SubscriptionType', related_name='TTFSST', on_delete=models.PROTECT)

