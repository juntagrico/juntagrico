from django.db import models
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel
from juntagrico.entity.depot import Tour
from juntagrico.entity.subtypes import SubscriptionSize


class Delivery(JuntagricoBaseModel):
    """
    Delivery for a specific tour and subscription size
    """
    delivery_date = models.DateField(_('Lieferdatum'))
    tour = models.ForeignKey(Tour, verbose_name=_('Ausfahrt'), on_delete=models.PROTECT, null=True, blank=True, default=None)
    subscription_size = models.ForeignKey(SubscriptionSize,
                                          verbose_name=_('{0}-Grösse').format(Config.vocabulary('subscription')),
                                          on_delete=models.PROTECT)

    def __str__(self):
        return u"%s - %s - %s" % (self.delivery_date, self.tour or _('Keine'), self.subscription_size.long_name)

    class Meta:
        verbose_name = _('Lieferung')
        verbose_name_plural = _('Lieferungen')
        constraints = [
            models.UniqueConstraint(fields=['delivery_date', 'tour', 'subscription_size'], name='unique_delivery'),
        ]


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
