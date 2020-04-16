from django.utils import timezone

from juntagrico.signals import extra_sub_activated, extra_sub_deactivated
from juntagrico.util.lifecycle import handle_activated_deactivated


def extra_sub_pre_save(sender, instance, **kwargs):
    handle_activated_deactivated(instance, sender, extra_sub_activated, extra_sub_deactivated)

