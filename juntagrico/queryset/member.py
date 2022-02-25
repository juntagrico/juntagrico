from datetime import date

from django.db.models import QuerySet, Sum, Case, When, Q, DecimalField
from django.utils import timezone

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
        return self.filter(assignments__job=job)

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

    def annotate_assignment_count(self, until=None):
        until = until or end_of_business_year()
        if isinstance(until, date):
            until = {'assignments__job__time__date__lte': until}
        else:
            until = {'assignments__job__time__lte': until}
        cond = dict(
            assignments__job__time__date__gte=start_of_business_year(),
            **until,
            then='assignments__amount'
        )
        default = dict(default=0, output_field=DecimalField())
        return self.annotate(
            assignment_count=Sum(Case(When(**cond), **default))
        ).annotate(
            core_assignment_count=Sum(Case(When(**cond, assignments__core_cache=True), **default))
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
