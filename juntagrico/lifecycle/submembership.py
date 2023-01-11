from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config


def sub_membership_pre_save(sender, instance, **kwargs):
    check_sub_membership_consistency(instance)


def check_submembership_dates(instance):
    now = timezone.now().date()
    has_joined = instance.join_date is not None
    has_left = instance.leave_date is not None
    join_date = instance.join_date or now
    leave_date = instance.leave_date or join_date  # allow future join dates
    if has_left and not has_joined:
        raise ValidationError(_('Bitte "Beitrittsdatum" ausfüllen'), code='invalid')
    if not (join_date <= leave_date):
        raise ValidationError(_('Datenreihenfolge stimmt nicht.'), code='invalid')


def check_submembership_parent_dates(instance):
    subscription = instance.subscription
    s_activated = subscription.activation_date is not None
    m_joined = instance.join_date is not None
    s_deactivated = subscription.deactivation_date is not None
    m_left = instance.leave_date is not None
    wrong_start = (m_joined and s_activated and subscription.activation_date > instance.join_date) or (not s_activated and m_joined)
    wrong_end = (m_left and s_deactivated and subscription.deactivation_date < instance.leave_date) or (s_deactivated and not m_left)
    if wrong_start:
        raise ValidationError(_('Beitrittsdatum des Bestandteils passt nicht zum übergeordneten Aktivierungsdatum'), code='invalid')
    if wrong_end:
        raise ValidationError(_('Austrittsdatum des Bestandteils passt nicht zum übergeordneten Deaktivierungsdatum'), code='invalid')


def check_sub_membership_consistency(instance):
    check_submembership_dates(instance)
    check_submembership_parent_dates(instance)
    subscription = instance.subscription
    try:
        member = instance.member
    except AttributeError:
        raise ValidationError(
            _('Kein/e/n gültige/n/s {} angegeben').format(Config.vocabulary('member')),
            code='invalid')
    check_sub_membership_consistency_ms(member, subscription, instance.join_date, instance.leave_date)


def check_sub_membership_consistency_ms(member, subscription, join_date, leave_date):
    from juntagrico.entity.member import SubscriptionMembership
    # check for subscription membership overlaps
    memberships = SubscriptionMembership.objects.exclude(subscription=subscription).filter(member=member)
    if join_date is None:
        check = Q(leave_date__isnull=True)
    elif leave_date is None:
        check = Q(leave_date__isnull=True) | Q(leave_date__gte=join_date)
    else:
        check = Q(join_date__lte=leave_date, leave_date__gte=leave_date) | \
            Q(join_date__lte=join_date, leave_date__gte=join_date)
    if memberships.filter(check).exists():
        raise ValidationError(
            _('Diese/r/s {} hat ein/e/n zeitlich überlappende/n/s {}').format(Config.vocabulary('member'),
                                                                              Config.vocabulary('subscription')),
            code='invalid')
