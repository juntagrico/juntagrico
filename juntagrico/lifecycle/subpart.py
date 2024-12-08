from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from juntagrico.signals import sub_part_activated, sub_part_deactivated
from juntagrico.util.lifecycle import handle_activated_deactivated


def check_sub_part_consistency(instance):
    # keep part deactivation date consistent with subscription deactivation date
    sub_deactivation_date = instance.subscription.deactivation_date
    if sub_deactivation_date is not None and instance.deactivation_date is None:
        instance.deactivation_date = sub_deactivation_date
    # check consistency
    instance.check_date_order()
    check_subpart_parent_dates(instance, instance.subscription)


def check_subpart_parent_dates(instance, subscription, check_empty_end=True):
    s_activated = subscription.activation_date is not None
    p_activated = instance.activation_date is not None
    wrong_start = (p_activated and s_activated and subscription.activation_date > instance.activation_date) or (not s_activated and p_activated)
    if wrong_start:
        raise ValidationError(_('Aktivierungsdatum des Bestandteils passt nicht zum übergeordneten Aktivierungsdatum'), code='part_activation_date_mismatch')
    s_deactivated = subscription.deactivation_date is not None
    p_deactivated = instance.deactivation_date is not None
    wrong_end = (
        p_deactivated and s_deactivated and subscription.deactivation_date < instance.activation_date
    ) or (
        check_empty_end and s_deactivated and not p_deactivated
    )
    if wrong_end:
        raise ValidationError(_('Deaktivierungsdatum des Bestandteils passt nicht zum übergeordneten Deaktivierungsdatum'), code='part_deactivation_date_mismatch')


def sub_part_pre_save(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        check_sub_part_consistency(instance)
        handle_activated_deactivated(instance, sender, sub_part_activated, sub_part_deactivated)
