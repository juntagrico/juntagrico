from juntagrico.signals import extra_sub_activated, extra_sub_deactivated
from juntagrico.util.lifecycle import handle_activated_deactivated


def check_extra_sub_consistency(instance):
    instance.check_date_order()


def extra_sub_pre_save(sender, instance, **kwargs):
    check_extra_sub_consistency(instance)
    handle_activated_deactivated(instance, sender, extra_sub_activated, extra_sub_deactivated)
