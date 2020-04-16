from juntagrico.signals import sub_part_activated, sub_part_deactivated
from juntagrico.util.lifecycle import handle_activated_deactivated


def sub_part_pre_save(sender, instance, **kwargs):
    handle_activated_deactivated(instance, sender, sub_part_activated, sub_part_deactivated)
