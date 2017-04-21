# encoding: utf-8

from django.db import models

from juntagrico.entity.billing import *

class ExtraSubscriptionType(models.Model):
    """
    Types of extra subscriptions, e.g. eggs, cheese, fruit
    """
    name = models.CharField("Name", max_length=100, unique=True)
    size = models.CharField("Groesse (gross,4, ...)", max_length=100, default="")
    description = models.TextField("Beschreibung", max_length=1000)
    sort_order = models.FloatField("Groesse zum Sortieren", default=1.0)
    category = models.ForeignKey("ExtraSubscriptionCategory", related_name="category", null=True, blank=True,
                                 on_delete=models.PROTECT)

    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)

    class Meta:
        verbose_name = "Zusatz-Abo-Typ"
        verbose_name_plural = "Zusatz-Abo-Typen"


class ExtraSubscriptionCategory(models.Model):
    """
    Types of extra subscriptions, e.g. eggs, cheese, fruit
    """
    name = models.CharField("Name", max_length=100, unique=True)
    description = models.TextField("Beschreibung", max_length=1000, blank=True)
    sort_order = models.FloatField("Nummer zum Sortieren", default=1.0)

    def __unicode__(self):
        return u"%s %s" % (self.id, self.name)

    class Meta:
        verbose_name = "Zusatz-Abo-Kategorie"
        verbose_name_plural = "Zusatz-Abo-Kategorien"


class ExtraSubscription(Billable):
    """
    Types of extra subscriptions, e.g. eggs, cheese, fruit
    """
    main_subscription = models.ForeignKey("Subscription", related_name="extra_subscription_set", null=False,
                                          blank=False,
                                          on_delete=models.PROTECT)
    active = models.BooleanField(default=False)
    canceled = models.BooleanField("gekündigt", default=False)
    activation_date = models.DateField("Aktivierungssdatum", null=True, blank=True)
    deactivation_date = models.DateField("Deaktivierungssdatum", null=True, blank=True)
    type = models.ForeignKey(ExtraSubscriptionType, related_name="extra_subscriptions", null=False, blank=False,
                             on_delete=models.PROTECT)

    old_active = None

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        if instance.old_active != instance.active and instance.old_active is False and instance.deactivation_date is None:
            instance.activation_date = timezone.now().date()
        elif instance.old_active != instance.active and instance.old_active is True and instance.deactivation_date is None:
            instance.deactivation_date = timezone.now().date()

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_active = instance.active

    def __unicode__(self):
        return u"%s %s" % (self.id, self.type.name)

    class Meta:
        verbose_name = "Zusatz-Abo"
        verbose_name_plural = "Zusatz-Abos"