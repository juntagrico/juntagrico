from django.db import models
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel
from juntagrico.entity.subtypes import SubscriptionSize
from juntagrico.util.temporal import weekday_short


class Delivery(JuntagricoBaseModel):
    """
    Delivery with a specific date (usually Tuesday or Thursday)
    """
    delivery_date = models.DateField(_('Lieferdatum'))
    subscription_size = models.ForeignKey(SubscriptionSize,
                                          verbose_name=_('{0}-Grösse').format(Config.vocabulary('subscription')),
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
        verbose_name = _('Lieferung')
        verbose_name_plural = _('Lieferungen')
        unique_together = ("delivery_date", "subscription_size")


class DeliveryItem(JuntagricoBaseModel):
    delivery = models.ForeignKey(Delivery, verbose_name=_('Lieferung'),
                                 related_name='items',
                                 on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=100, default="")
    amount = models.CharField(_('Menge'), max_length=100, default="")
    comment = models.CharField(_('Kommentar'), max_length=1000,
                               default="", blank=True)

    class Meta:
        verbose_name = _('Lieferobjekt')
        verbose_name_plural = _('Lieferobjekte')
