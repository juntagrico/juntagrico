from django.db import models

from juntagrico.util.temporal import weekday_short
from juntagrico.entity.subs import SubscriptionSize


class Delivery(models.Model):
    """
    Delivery with a specific date (usually Tuesday or Thursday)
    """
    delivery_date = models.DateField("Lieferdatum")
    subscription_size = models.ForeignKey(SubscriptionSize,
                                          verbose_name='Abo-Grösse',
                                          on_delete=models.PROTECT)

    def __str__(self):
        return u"%s - %s" % (self.delivery_date,
                             self.subscription_size.long_name)

    def weekday(self):
        return self.delivery_date.isoweekday()

    def weekday_shortname(self):
        day = self.delivery_date.isoweekday()
        return weekday_short(day, 2)

    class Meta:
        verbose_name = 'Lieferung'
        verbose_name_plural = 'Lieferungen'
        unique_together = ("delivery_date", "subscription_size")


class DeliveryItem(models.Model):
    delivery = models.ForeignKey(Delivery, verbose_name='Lieferung',
                                 related_name='items',
                                 on_delete=models.CASCADE)
    name = models.CharField("Name", max_length=100, default="")
    amount = models.CharField("Menge", max_length=100, default="")
    comment = models.CharField("Kommentar", max_length=1000,
                               default="", blank=True)

    class Meta:
        verbose_name = 'Lieferobjekt'
        verbose_name_plural = 'Lieferobjekte'
