from django.utils import timezone

from juntagrico.signals import extra_sub_activated, extra_sub_deactivated
from juntagrico.util.lifecycle import handle_activated_deactivated


def extra_sub_pre_save(sender, instance, **kwargs):
    handle_activated_deactivated(instance, sender, extra_sub_activated, extra_sub_deactivated)


def handle_extra_sub_activated(sender, instance, **kwargs):
    instance.activation_date = instance.activation_date if instance.activation_date is not None else timezone.now().date()


def handle_extra_sub_deactivated(sender, instance, **kwargs):
    instance.deactivation_date = instance.deactivation_date if instance.deactivation_date is not None else timezone.now().date()
