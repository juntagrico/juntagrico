# encoding: utf-8

from django.db import models
from juntagrico.util.temporal import weekdays
from juntagrico.entity.subs import SubscriptionSize

class Delivery(models.Model):
    """
    Delivery with a specific date (usually Tuesday or Thursday)
    """
    delivery_date = models.DateField("Lieferdatum")
    subscription_size = models.ForeignKey(SubscriptionSize, verbose_name='Abo-Grösse', on_delete=models.PROTECT)
    text = models.TextField("Gemüseliste", max_length=1000, default="", null=True, blank=True) # JSON-serialized (text) version of your list
    # json = JSONEditableField()
    
    def __str__(self):
        return u"%s - %s" % (self.delivery_date, self.subscription_size)
    
    def weekday(self):
        return self.delivery_date.isoweekday()
    
    def weekday_shortname(self):
        weekday = weekdays[self.delivery_date.isoweekday()]
        return weekday[:2]
    
    class Meta:
        verbose_name = 'Lieferung'
        verbose_name_plural = 'Lieferungen'
        unique_together = (("delivery_date", "subscription_size"))