import datetime

from django.db.models import QuerySet, Sum, Case, When, Prefetch, F, Q, Count, Exists, OuterRef
from django.utils.decorators import method_decorator
from django.utils.itercompat import is_iterable

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

    def canceled(self):
        return self.filter(
            cancellation_date__isnull=False,
            deactivation_date__isnull=True
        )

    def has_active_subscription(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.filter(
            q_subscription_activated(on_date),
            ~q_subscription_deactivated(on_date),
            q_joined_subscription(on_date),
            ~q_left_subscription(on_date)
        )

    def in_depot(self, depot):
        if is_iterable(depot):
            return self.filter(subscriptions__depot__in=depot)
        return self.filter(subscriptions__depot=depot)

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
        members = self.defer('notes').prefetch_related('areas').annotate(userid=F('user__id'))
        # prefetch current subscription. This will be picked up in Member.subscription_current()
        from juntagrico.entity.subs import Subscription
        return members.prefetch_related(
            Prefetch(
                'subscriptions',
                queryset=Subscription.objects.joined().annotate(depot_name=F('depot__name')),
                to_attr='current_subscription'
            ),
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
        return [f'{m} <{m.email}>' for m in self]
