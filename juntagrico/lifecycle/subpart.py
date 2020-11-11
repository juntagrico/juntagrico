from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

from juntagrico.signals import sub_part_activated, sub_part_deactivated
from juntagrico.util.lifecycle import handle_activated_deactivated


def check_sub_part_consistency(instance):
    instance.check_date_order()
    check_subpart_parent_dates(instance, instance.subscription)


def check_subpart_parent_dates(instance, subscription):
    s_activated = subscription.activation_date is not None
    p_activated = instance.activation_date is not None
    s_deactivated = subscription.deactivation_date is not None
    p_deactivated = instance.deactivation_date is not None
    wrong_start = (p_activated and s_activated and subscription.activation_date > instance.activation_date) or (not s_activated and p_activated)
    wrong_end = (p_deactivated and s_deactivated and subscription.deactivation_date < instance.activation_date) or(s_deactivated and not p_deactivated)
    if wrong_start:
        raise ValidationError(_('Aktivierungsdatum des Bestandteils passt nicht zum übergeordneten Aktivierungsdatum'), code='invalid')
    if wrong_end:
        raise ValidationError(_('Deaktivierungsdatum des Bestandteils passt nicht zum übergeordneten Deaktivierungsdatum'), code='invalid')


def sub_part_pre_save(sender, instance, **kwargs):
    check_sub_part_consistency(instance)
    handle_activated_deactivated(instance, sender, sub_part_activated, sub_part_deactivated)
