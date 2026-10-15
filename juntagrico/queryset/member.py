import datetime
import re

from django.contrib.auth.models import Permission
from django.db.models import (
    QuerySet,
    Sum,
    Case,
    When,
    Prefetch,
    F,
    Q,
    Count,
    Exists,
    OuterRef,
    Value,
    Subquery,
)
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.utils.itercompat import is_iterable
from django.utils.translation import gettext as _

from juntagrico.util.temporal import default_to_business_year
from . import SubscriptionMembershipQuerySetMixin


def q_joined_subscription(on_date=None):
    on_date = on_date or datetime.date.today()
    return Q(subscriptionmembership__join_date__isnull=False,
             subscriptionmembership__join_date__lte=on_date)


def q_left_subscription(on_date=None):
    on_date = on_date or datetime.date.today()
    return Q(subscriptionmembership__leave_date__isnull=False,
             subscriptionmembership__leave_date__lte=on_date)


def q_subscription_activated(on_date=None):
    on_date = on_date or datetime.date.today()
    return Q(subscriptions__activation_date__isnull=False,
             subscriptions__activation_date__lte=on_date)


def q_subscription_deactivated(on_date=None):
    on_date = on_date or datetime.date.today()
    return Q(subscriptions__deactivation_date__isnull=False,
             subscriptions__deactivation_date__lte=on_date)


class MemberQuerySet(SubscriptionMembershipQuerySetMixin, QuerySet):
    def active(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.exclude(deactivation_date__lte=on_date)

    def inactive(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.filter(deactivation_date__lte=on_date)

    def canceled(self):
        return self.filter(
            cancellation_date__isnull=False,
            deactivation_date__isnull=True
        )

    def has_active_subscription(self, on_date=None, in_depot=None):
        on_date = on_date or datetime.date.today()
        depot_query = []
        if in_depot is not None:
            if is_iterable(in_depot):
                depot_query.append(Q(subscriptions__depot__in=in_depot))
            else:
                depot_query.append(Q(subscriptions__depot=in_depot))
        return self.filter(
            q_subscription_activated(on_date),
            ~q_subscription_deactivated(on_date),
            q_joined_subscription(on_date),
            ~q_left_subscription(on_date),
            *depot_query
        )

    def has_active_shares(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.filter(
            Q(share__termination_date__isnull=True) | Q(share__termination_date__gt=on_date),
            share__isnull=False,
        )

    def annotate_job_slots(self):
        return self.annotate(slots=Count('id')).distinct()

    def annotate_first_job(self, suffix='', of_jobs=None):
        from juntagrico.entity.jobs import Assignment
        of_jobs = {'job__in': of_jobs} if of_jobs is not None else {}
        return self.annotate(**{
            f'is_first_job{suffix}': ~Exists(
                Assignment.objects.filter(
                    member=OuterRef('pk'),
                    job__time__lt=OuterRef('jobs__time'),
                    **of_jobs
                )
            )
        })

    def prefetch_for_list(self):
        members = self.defer('notes').select_user().prefetch_related('areas')
        # prefetch current subscription. This will be picked up in Member.subscription_current()
        from juntagrico.entity.subs import Subscription
        return members.prefetch_related(
            Prefetch(
                'subscriptions',
                queryset=Subscription.objects.joined().annotate(
                    # DEPRECATED: depot is prefetched. use depot.name instead.
                    depot_name=F('depot__name')
                ).cache_content(),
                to_attr='current_subscription',
            ),
        )

    def annotate_membership_status(self):
        from ..entity.membership import Membership
        today = datetime.date.today()
        membership = Membership.objects.filter(
            account=OuterRef('pk'),
        )
        active_membership = membership.active(today)
        requested_membership = membership.requested(today)
        return self.annotate(
            membership_status=Case(
                When(
                    Exists(active_membership),
                    then=Value(_('aktiv')),
                ),
                When(
                    Exists(requested_membership),
                    then=Value(_('wartend')),
                ),
                default=Value(_('nein')),
            )
        )

    def annotate_membership(self):
        from juntagrico.entity.membership import Membership
        return self.annotate(
            has_uncanceled_membership=Exists(
                Membership.objects.not_canceled().filter(
                    account=OuterRef('pk'),
                )
            )
        )
  
    @method_decorator(default_to_business_year)
    def annotate_assignment_count(self, start=None, end=None, prefix='', **extra_filters):
        """
        counts assignments completed within period of interest.
        :param start: start date of period of interest. Default: Start of current business year.
        :param end: end date of period of interest. Default: End of current business year.
        :param prefix: optional. prefix for the annotation name.
        :param extra_filters: optional. additional filter applied to annotation of assignemnts.
        :return: member queryset with annotated assignment count in `assignment_count`
        """
        return self.annotate(**{
            prefix + 'assignment_count': Sum(
                Case(
                    When(
                        **extra_filters,
                        assignment__job__time__date__range=(start, end),
                        then='assignment__amount'
                    ),
                    default=0.0
                )
            )
        })

    def annotate_core_assignment_count(self, start=None, end=None, prefix='', **extra_filters):
        return self.annotate_assignment_count(start, end, prefix + 'core_', assignment__core_cache=True, **extra_filters)

    def annotate_all_assignment_count(self, start=None, end=None, prefix='', **extra_filters):
        """
        Convenience method. Applies annotate_assignment_count and annotate_core_assignment_count
        """
        return self.annotate_assignment_count(start, end, prefix, **extra_filters)\
            .annotate_core_assignment_count(start, end, prefix, **extra_filters)

    def as_email_recipients(self):
        allowed = re.compile(r"[^\w \-._']", flags=re.UNICODE)
        return [f'{allowed.sub("", str(m))} <{m.email}>' for m in self]

    def by_permission(self, permission_codename):
        perm = Permission.objects.get(codename=permission_codename)
        return self.filter(Q(user__groups__permissions=perm) | Q(user__user_permissions=perm)).distinct()

    def select_user(self):
        return self.select_related('user')

    def annotate_shares(self, **kwargs):
        from juntagrico.entity.share import Share
        if not kwargs:
            kwargs = {'ordered_shares': 'unpaid.usable', 'paid_shares': 'active', 'canceled_shares': 'active.canceled'}
        qs = self
        for to_attr, filters in kwargs.items():
            share_qs = Share.objects
            for f in filters.split('.'):
                share_qs = getattr(share_qs, f)()
            qs = qs.annotate(
                **{
                    to_attr: Coalesce(
                        Subquery(
                            share_qs
                            .filter(member=OuterRef('pk'))
                            .values('member')
                            .annotate(count=Count('id'))
                            .values('count')
                        ),
                        0,
                    )
                }
            )
        return qs
