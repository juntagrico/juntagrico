import datetime

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext as _

from juntagrico.config import Config


def sub_membership_pre_save(sender, instance, **kwargs):
    check_sub_membership_consistency(instance)


def check_submembership_dates(instance):
    has_joined = instance.join_date is not None
    has_left = instance.leave_date is not None
    join_date = instance.join_date or datetime.date.today()
    leave_date = instance.leave_date or join_date  # allow future join dates
    if has_left and not has_joined:
        raise ValidationError(_('Bitte "Beitrittsdatum" ausfüllen'), code='invalid')
    if not (join_date <= leave_date):
        raise ValidationError(_('Datenreihenfolge stimmt nicht.'), code='invalid')


def check_sub_membership_consistency(instance):
    check_submembership_dates(instance)
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
            _('{} kann nur 1 {} gleichzeitig haben.').format(Config.vocabulary('member'),
                                                             Config.vocabulary('subscription')),
            code='invalid')
