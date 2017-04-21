# encoding: utf-8

from django.db import models
from polymorphic.models import PolymorphicModel


class Billable(PolymorphicModel):
    """
    Parent type for billables.
    """

    class Meta:
        verbose_name = 'Verrechenbare Einheit'
        verbose_name_plural = 'Verrechenbare Einhaiten'


class Bill(models.Model):
    """
    Actuall Bill for billables
    """
    billable = models.ForeignKey("Billable", related_name="bills", null=False, blank=False,
                                 on_delete=models.PROTECT)
    paid = models.BooleanField("bezahlt", default=False)
    bill_date = models.DateField("Aktivierungssdatum", null=True, blank=True)
    ref_number = models.CharField("Referenznummer", max_length=30, unique=True)
    amount = models.FloatField("Betrag", null=False, blank=False)

    def __unicode__(self):
        return u"%s %s" % self.ref_number

    class Meta:
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"


class Payment(models.Model):
    """
    Payment for bill
    """
    bill = models.ForeignKey("Bill", related_name="payments", null=False, blank=False,
                             on_delete=models.PROTECT)
    paid_date = models.DateField("Bezahldatum", null=True, blank=True)
    amount = models.FloatField("Betrag", null=False, blank=False)

    def __unicode__(self):
        return u"%s %s" % self.ref_number

    class Meta:
        verbose_name = "Zahlung"
        verbose_name_plural = "Zahlung"
