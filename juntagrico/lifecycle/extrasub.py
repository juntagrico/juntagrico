from django.utils import timezone

from juntagrico.config import Config
from juntagrico.signals import extra_sub_activated, extra_sub_deactivated
from juntagrico.util.bills import bill_extra_subscription


def extra_sub_pre_save(sender, instance, **kwargs):
    if instance._old['active'] != instance.active and instance._old['active'] is False and instance.deactivation_date is None:
        extra_sub_activated.send(sender=sender, instance=instance)
    elif instance._old['active'] != instance.active and instance._old['active'] is True and instance.deactivation_date is None:
        extra_sub_deactivated.send(sender=sender, instance=instance)


def handle_extra_sub_activated(sender, instance, **kwargs):
    instance.activation_date = instance.activation_date if instance.activation_date is not None else timezone.now().date()
    if Config.billing():
        bill_extra_subscription(instance)


def handle_extra_sub_deactivated(sender, instance, **kwargs):
        instance.deactivation_date = instance.deactivation_date if instance.deactivation_date is not None else timezone.now().date()
