from datetime import datetime, time

from django.db.models import QuerySet, Sum, Case, When, Q
from django.utils import timezone
from django.utils.timezone import get_default_timezone as gdtz

from juntagrico.util.models import PropertyQuerySet, q_deactivated
from juntagrico.util.models import q_cancelled
from juntagrico.util.temporal import start_of_business_year, end_of_business_year


class MemberQuerySet(QuerySet):
    def all(self):
        result = PropertyQuerySet.from_qs(super().all())
        result.set_property('name', 'all')
        result.set_property('subscription_id', '')
        return result

    def active(self):
        return self.filter(~q_deactivated())

    def canceled(self):
        return self.filter(q_cancelled()).exclude(q_deactivated())

    def with_subscription(self):
        return self.filter(has_subscription() | has_cancelled_subscription())

    def with_future_subscription(self):
        return self.filter(has_future_subscription())

    def joined_subscription(self):
        return self.filter(q_joined_subscription(), ~q_left_subscription())

    def joining_subscription(self):
        return self.filter(~q_left_subscription())

    def in_depot(self, depot):
        return self.active().with_subscription().filter(subscription__depot=depot)

    def in_job(self, job):
        return self.filter(assignment__job=job)

    def available_for_subscription(self, subscription):
        result = PropertyQuerySet.from_qs(self.filter(
            (~has_subscription() & ~has_cancelled_subscription() & ~has_future_subscription()) | Q(
                subscription=subscription)).distinct())
        result.set_property('name', 's')
        result.set_property('subscription_id', str(subscription.pk))
        return result

    def available_for_future_subscription(self, subscription=None):
        filters = (~has_subscription() | has_cancelled_subscription()) & ~has_future_subscription()
        if subscription:
            filters |= Q(subscription=subscription)
        result = PropertyQuerySet.from_qs(self.filter(filters).distinct())
        result.set_property('name', 'fs' if subscription else 'cs')
        result.set_property('subscription_id', str(subscription.pk) if subscription else '')
        return result

    def get_by_email(self, email):
        return next(iter(self.filter(email__iexact=email) or []), None)

    def by_permission(self, permission_codename):
        return self.filter(
            Q(user__groups__permissions__codename=permission_codename) | Q(user__user_permissions__codename=permission_codename)
        ).distinct()

    def annotate_assignment_count(self):
        start = datetime.combine(start_of_business_year(), time.min, tzinfo=gdtz())
        end = datetime.combine(end_of_business_year(), time.min, tzinfo=gdtz())
        cond = dict(
            assignment__job__time__gte=start,
            assignment__job__time__lt=end,
            then='assignment__amount'
        )
        return self.annotate(
            assignment_count=Sum(Case(When(**cond)))
        ).annotate(
            core_assignment_count=Sum(Case(When(**cond, assignment__core_cache=True)))
        )


def q_joined_subscription():
    return Q(subscriptionmembership__join_date__isnull=False,
             subscriptionmembership__join_date__lte=timezone.now().date())


def q_left_subscription():
    return Q(subscriptionmembership__leave_date__isnull=False,
             subscriptionmembership__leave_date__lte=timezone.now().date())


def q_subscription_activated():
    return Q(subscription__activation_date__isnull=False,
             subscription__activation_date__lte=timezone.now().date())


def q_subscription_cancelled():
    return Q(subscription__cancellation_date__isnull=False,
             subscription__cancellation_date__lte=timezone.now().date())


def q_subscription_deactivated():
    return Q(subscription__deactivation_date__isnull=False,
             subscription__deactivation_date__lte=timezone.now().date())


def has_subscription():
    return Q(q_subscription_activated(),
             ~q_subscription_cancelled(),
             ~q_subscription_deactivated(),
             q_joined_subscription(),
             ~q_left_subscription())


def has_cancelled_subscription():
    return Q(q_subscription_activated(),
             q_subscription_cancelled(),
             ~q_subscription_deactivated(),
             q_joined_subscription(),
             ~q_left_subscription())


def has_future_subscription():
    return Q(~q_subscription_activated(),
             ~q_subscription_cancelled(),
             ~q_subscription_deactivated(),
             subscriptionmembership__isnull=False)
