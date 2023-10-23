from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from juntagrico.signals import sub_part_activated, sub_part_deactivated
from juntagrico.util.lifecycle import handle_activated_deactivated


def check_sub_part_consistency(instance):
    instance.check_date_order()


def sub_part_pre_save(sender, instance, **kwargs):
    check_sub_part_consistency(instance)
    handle_activated_deactivated(instance, sender, sub_part_activated, sub_part_deactivated)
