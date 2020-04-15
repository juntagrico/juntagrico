from django.utils import timezone

from juntagrico.signals import sub_part_activated, sub_part_deactivated
from juntagrico.util.lifecycle import handle_activated_deactivated


def sub_part_pre_save(sender, instance, **kwargs):
    handle_activated_deactivated(instance, sender, sub_part_activated, sub_part_deactivated)


def handle_sub_part_activated(sender, instance, **kwargs):
    instance.activation_date = instance.activation_date or timezone.now().date()


def handle_sub_part_deactivated(sender, instance, **kwargs):
    instance.deactivation_date = instance.deactivation_date or timezone.now().date()
