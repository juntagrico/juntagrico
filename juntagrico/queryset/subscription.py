import datetime

from django.db import connection
from django.db.models import When, Q, F, ExpressionWrapper, DurationField, Case, DateField, FloatField, Sum, Subquery, \
    OuterRef, PositiveIntegerField
from django.db.models.functions import Least, Greatest, Round, Cast, Coalesce, ExtractDay
from django.utils.decorators import method_decorator
from polymorphic.query import PolymorphicQuerySet

from juntagrico.entity import SimpleStateModelQuerySet
from juntagrico.entity.member import SubscriptionMembership
from juntagrico.util.temporal import default_to_business_year
from . import SubscriptionMembershipQuerySetMixin


def assignments_in_subscription_membership(start, end, **extra_filters):
    """
    Based on example in documentation
    https://docs.djangoproject.com/en/4.1/ref/models/expressions/#using-aggregates-within-a-subquery-expression
    :param start: beginning of period of interest
    :param end: end of period of interest
    :param extra_filters: additional filters to apply on SubscriptionMembership selection
    :return: a queryset returning the sub of the assignments amounts, ready for use in a subquery of a subscription
    """
    return SubscriptionMembership.objects.filter(subscription=OuterRef('pk')).filter(
        Q(leave_date__isnull=True) |
        Q(leave_date__gte=F('member__assignment__job__time__date')),
        join_date__lte=F('member__assignment__job__time__date'),
        member__assignment__job__time__date__range=(start, end),
        **extra_filters
    ).order_by().values('subscription').annotate(
        total=Sum('member__assignment__amount', default=0.0),
    ).values('total')


class SubscriptionQuerySet(SubscriptionMembershipQuerySetMixin, SimpleStateModelQuerySet, PolymorphicQuerySet):
    microseconds_in_day = 24 * 3600 * 10 ** 6
    days_in_year = 365  # ignore leap years
    one_day = datetime.timedelta(1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_required = False
        self._end_required = False

    def active(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.in_date_range(on_date, on_date).exclude(activation_date=None)

    def in_date_range(self, start, end):
        """
        subscriptions that were active in the given period
        """
        return self.exclude(deactivation_date__lt=start).exclude(activation_date__gt=end)

    def activate_future_depots(self):
        for subscription in self.exclude(future_depot__isnull=True):
            subscription.activate_future_depot()

    @method_decorator(default_to_business_year)
    def annotate_assignment_counts(self, start=None, end=None, of_member=None, prefix=''):
        """
        count assignments of the subscription members for the jobs they did within their subscription membership and in the period of interest.
        :param start: beginning of period of interest, default: start of current business year.
        :param end: end of period of interest, default: end of current business year.
        :param of_member: if set, only assignments of the given member are counted.
        :param prefix: prefix for the resulting attribute names, default=''.
        :return: the queryset of subscriptions with annotations `assignment_count` and `core_assignment_count`.
        """
        # Using subquery as otherwise the sum would be wrong when used in combination with the annotations of annotate_required_assignments
        member = {'member': of_member} if of_member else {}
        return self.annotate(**{
            prefix + 'assignment_count': Coalesce(Subquery(assignments_in_subscription_membership(start, end, **member)), 0.0),
            prefix + 'core_assignment_count': Coalesce(Subquery(assignments_in_subscription_membership(
                start, end,
                member__assignment__core_cache=True,
                **member
            )), 0.0)
        })

    @method_decorator(default_to_business_year)
    def annotate_required_assignments(self, start=None, end=None):
        """
        calculate the required number of (core) assignments of the subscription given the parts in it, discounted with their duration within the period of interest.
        :param start: beginning of period of interest, default: start of current business year.
        :param end: end of period of interest, default: end of current business year.
        :return: the queryset of subscriptions with annotations `required_assignments` and `required_core_assignments`.
        """
        if self._start_required is False and self._end_required is False:
            # first run: remember date range and apply annotations
            self._start_required = start
            self._end_required = end
        elif self._start_required == start and self._end_required == end:
            # not first run and date range matches. No need to reapply annotations.
            return self
        else:
            raise ValueError('required assignments can not be assigned twice with 2 different date ranges.')

        return self.alias(
            # convert trial days into duration. Minus 1 to end up at the end of the last trial day, e.g., 1. + 30 days = 30. (not 31.)
            parts__type__trial_duration=(
                # tested with postgreSQL
                ExpressionWrapper(F('parts__type__trial_days') * self.one_day, DurationField()) - self.one_day
                if connection.features.has_native_duration_field else
                # alternative tested with MariaDB and Sqlite
                Cast(F('parts__type__trial_days') * self.microseconds_in_day, DurationField()) - self.one_day
            ),
            # find (assumed) deactivation date of part
            parts__forecast_final_date=Least(
                end,  # limit final date to period of interest
                Case(
                    # use deactivation date if set
                    When(parts__deactivation_date__isnull=False,
                         then='parts__deactivation_date'),
                    # on trial subs without deactivation date assume they will last for trial duration.
                    When(parts__type__trial_days__gt=0,
                         then=Cast(F('parts__activation_date') + F('parts__type__trial_duration'), DateField())),
                    # otherwise default to end of period
                    default=end,
                    output_field=DateField()
                )
            ),
            # number of days subscription part is actually active within period of interest. Add a day because activation day should also count to duration
            parts__duration_in_period=F('parts__forecast_final_date') - Greatest('parts__activation_date', start) + self.one_day,
            parts__duration_in_period_float=Greatest(
                0.0,  # ignore values <0 resulting from parts outside the period of interest
                # Tested on postgreSQL (ExtractDay) and SQLite, MariaDB (Cast)
                ExtractDay('parts__duration_in_period')
                if connection.features.has_native_duration_field else
                Cast('parts__duration_in_period', FloatField()) / self.microseconds_in_day,
                output_field=FloatField()
            ),
            # number of days within which the assignments are required
            parts__reference_duration=Case(
                When(parts__type__trial_days__gt=0,
                     then='parts__type__trial_days'),
                default=self.days_in_year,
                output_field=FloatField()
            ),
            parts__required_assignments_discount=Case(
                # ignore parts that have not startet yet
                When(parts__activation_date__isnull=True,
                     then=0.0),
                # get discount ratio for required assignments
                default=F('parts__duration_in_period_float') / F('parts__reference_duration')
            )
        ).annotate(  # annotate the final results
            required_assignments=Round(Sum(F('parts__type__required_assignments') * F('parts__required_assignments_discount'), default=0.0)),
            required_core_assignments=Round(Sum(F('parts__type__required_core_assignments') * F('parts__required_assignments_discount'), default=0.0)),
        )

    @method_decorator(default_to_business_year)
    def annotate_assignments_progress(self, start=None, end=None, of_member=None, count_jobs_from=None, count_jobs_until=None, prefix=''):
        """
        annotate required and made assignments and calculated progress for core and in general
        :param start: beginning of period of interest, default: start of current business year.
        :param end: end of period of interest, default: end of current business year.
        :param of_member: if set, assignments are only counted for the given member.
        :param count_jobs_from: if set, `annotate_assignment_counts` will only count starting from this date instead of start.
        :param count_jobs_until: if set, `annotate_assignment_counts` will only count until this date instead of end.
        :param prefix: prefix for the resulting attribute names `assignment_count`, `core_assignment_count`, `assignments_progress`, `core_assignments_progress`. default=''
        :return: the queryset of subscriptions with annotations `assignment_count`, `core_assignment_count`, `required_assignments`, `required_core_assignments`,
        `assignments_progress` and `core_assignments_progress`.
        """
        return self.annotate_required_assignments(start, end).annotate_assignment_counts(
            count_jobs_from or start, count_jobs_until or end, of_member, prefix
        ).annotate(**{
            prefix + 'assignments_progress': Case(
                When(required_assignments=0,
                     then=100),
                default=F(prefix + 'assignment_count') / F('required_assignments') * 100,
                output_field=FloatField()
            ),
            prefix + 'core_assignments_progress': Case(
                When(required_core_assignments=0,
                     then=100),
                default=F(prefix + 'core_assignment_count') / F('required_core_assignments') * 100,
                output_field=FloatField()
            )
        })


class SubscriptionPartQuerySet(SimpleStateModelQuerySet):
    def is_normal(self):
        return self.filter(type__size__product__is_extra=False)

    def is_extra(self):
        return self.filter(type__size__product__is_extra=True)

    def ordered(self):
        return self.filter(activation_date=None)

    def cancelled(self):
        return self.filter(cancellation_date__isnull=False, deactivation_date=None)

    def waiting_or_active(self, date=None):
        date = date or datetime.date.today()
        return self.exclude(deactivation_date__lte=date)

    def active_on(self, date=None):
        date = date or datetime.date.today()
        current_week_number = date.isocalendar()[1] - 1
        return (super().active_on(date)
                .annotate(week_mod=ExpressionWrapper((current_week_number + F('type__offset')) % (F('type__interval')),
                                                     output_field=PositiveIntegerField())).filter(week_mod=0))

    def sorted(self):
        return self.order_by('type__size__product__is_extra', 'type__size__product',
                             F('deactivation_date').desc(nulls_first=True),
                             F('cancellation_date').desc(nulls_first=True),
                             F('activation_date').desc(nulls_first=True))

    def by_primary_member(self, member):
        return self.filter(subscription__primary_member=member)

    def on_depot_list(self):
        return self.filter(type__size__depot_list=True)
