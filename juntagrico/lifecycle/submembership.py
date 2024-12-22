import datetime

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext as _

from juntagrico.config import Config


def sub_membership_pre_save(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        check_sub_membership_consistency(instance)


def check_submembership_dates(instance):
    has_joined = instance.join_date is not None
    has_left = instance.leave_date is not None
    join_date = instance.join_date or datetime.date.today()
    leave_date = instance.leave_date or join_date  # allow future join dates
    if has_left and not has_joined:
        raise ValidationError(_('Bitte "Beitrittsdatum" ausfüllen'), code='missing_join_date')
    if not (join_date <= leave_date):
        raise ValidationError(_('Datenreihenfolge stimmt nicht.'), code='invalid')


def check_submembership_parent_dates(instance, check_empty_end=True):
    subscription = instance.subscription
    s_activated = subscription.activation_date is not None
    m_joined = instance.join_date is not None
    wrong_start = (m_joined and s_activated and subscription.activation_date > instance.join_date) or (not s_activated and m_joined)
    if wrong_start:
        raise ValidationError(_('Beitrittsdatum passt nicht zum übergeordneten Aktivierungsdatum'),
                              code='join_date_mismatch')
    s_deactivated = subscription.deactivation_date is not None
    m_left = instance.leave_date is not None
    wrong_end = (
        m_left and s_deactivated and subscription.deactivation_date < instance.leave_date
    ) or (
        check_empty_end and s_deactivated and not m_left
    )
    if wrong_end:
        raise ValidationError(_('Austrittsdatum passt nicht zum übergeordneten Deaktivierungsdatum'),
                              code='leave_date_mismatch')


def check_sub_membership_consistency(instance):
    if hasattr(instance, 'subscription'):
        subscription = instance.subscription
        # keep leave date consistent with deactivation date
        if subscription.deactivation_date is not None and instance.leave_date is None:
            instance.leave_date = subscription.deactivation_date
        # check consistency
        check_submembership_parent_dates(instance)
        if hasattr(instance, 'member'):
            check_sub_membership_consistency_ms(instance)
    check_submembership_dates(instance)


def check_sub_membership_consistency_ms(sub_membership):
    from juntagrico.entity.member import SubscriptionMembership
    # check for subscription membership overlaps
    memberships = SubscriptionMembership.objects.filter(member=sub_membership.member).exclude(pk=sub_membership.pk)
    join_date = sub_membership.join_date
    leave_date = sub_membership.leave_date
    if join_date is None:
        check = Q(join_date__isnull=True)
    elif leave_date is None:
        check = Q(leave_date__isnull=True) | Q(leave_date__gte=join_date)
    else:
        check = Q(join_date__lte=leave_date, leave_date__gte=leave_date) | \
            Q(join_date__lte=join_date, leave_date__gte=join_date)
    if memberships.filter(check).exists():
        raise ValidationError(
            _('{} kann nur 1 {} gleichzeitig haben.').format(
                Config.vocabulary('member'),
                Config.vocabulary('subscription')
            ),
            code='invalid'
        )
