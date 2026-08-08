import datetime

from django.core.exceptions import ValidationError
from django.db.models import Q, Max, Min
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity.member import Member
from juntagrico.lifecycle import parse_date


def pre_save(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        check_membership_consistency(instance)


def check_membership_consistency(instance):
    instance.check_date_order()
    if hasattr(instance, 'account'):
        memberships = instance.account.memberships.exclude(pk=instance.pk)
        activation_date = instance.activation_date
        deactivation_date = parse_date(instance.deactivation_date)
        today = datetime.date.today()
        if activation_date is None:
            # can only request membership if no other membership is active
            check = Q(deactivation_date__isnull=True) | Q(deactivation_date__gte=today)
        elif deactivation_date is None:
            # can only have active membership if no other membership is active at the same time
            check = Q(activation_date__isnull=False, deactivation_date__isnull=True) | Q(deactivation_date__gte=activation_date)
        else:
            check = Q(activation_date__lte=deactivation_date, deactivation_date__isnull=True) | \
                    Q(activation_date__lte=deactivation_date, deactivation_date__gte=deactivation_date) | \
                    Q(activation_date__lte=activation_date, deactivation_date__gte=activation_date)
            if deactivation_date >= today:
                check |= Q(activation_date__isnull=True)
        if memberships.filter(check).exists():
            raise ValidationError(
                _('{} kann nur 1 {} gleichzeitig aktiv oder beantragt haben.').format(
                    Config.vocabulary('member'),
                    Config.vocabulary('membership')
                ),
                code='overlap'
            )


def sync(sender, instance, **kwargs):
    if not (
        Config.enable_shares()
        and Config.enable_membership()
        and Config.membership('sync_shares')
        and Config.membership('required_shares') > 0
    ):
        return

    if isinstance(instance, Member):
        account = instance
    else:
        account = instance.member
    today = datetime.date.today()
    active_shares = account.shares.exclude(payback_date__lte=today)
    current_membership = account.memberships.active_or_requested().first()
    # clear duplicate memberships
    for duplicate in account.memberships.active_or_requested()[1:]:
        duplicate.delete()
    
    active_share_count = active_shares.count()
    if Config.cumulative_shares_for_membership():
        active_share_count -= account.required_shares_count

    if active_share_count >= Config.membership('required_shares'):
        # account with active share should have an active membership
        activation_date = active_shares.aggregate(
            paid_date=Min('paid_date'),
        )['paid_date']
        if current_membership is not None:
            # update existing membership
            current_membership.activation_date = activation_date
            current_membership.save()
        else:
            # check if old membership exists that should be extended
            if old_membership := account.memberships.filter(deactivation_date__isnull=False).order_by('-deactivation_date').first():
                old_membership.deactivation_date = None
                old_membership.save()
            else:
                # create new membership
                from juntagrico.entity.membership import Membership
                Membership.objects.create(
                    account=account,
                    activation_date=activation_date
                )

    elif current_membership is not None:
        # there are not enough active shares -> deactivate current membership
        dates = account.shares.aggregate(
            cancellation_date=Max('cancelled_date'),
            deactivation_date=Max('payback_date'),
        )
        current_membership.cancellation_date = current_membership.cancellation_date or dates['cancellation_date']
        current_membership.deactivation_date = dates['deactivation_date']
        current_membership.save()
