import datetime
import functools

from django.db.models import When, Q, F, ExpressionWrapper, DurationField, Case, DateField, FloatField, Sum
from django.db.models.functions import Least, Greatest, Round
from django.utils.decorators import method_decorator
from polymorphic.query import PolymorphicQuerySet

from juntagrico.util.temporal import default_to_business_year


class SubscriptionQuerySet(PolymorphicQuerySet):
    microseconds_in_day = 24 * 3600 * 10 ** 6

    @method_decorator(default_to_business_year)
    def annotate_assignment_counts(self, start=None, end=None, of_member=None, prefix=''):
        """
        count assignments of the subscription members for the jobs they did within their subscription membership and in the period of interest
        :param start: beginning of period of interest, default: start of current business year
        :param end: end of period of interest, default: end of current business year
        :param of_member: if set, assignments of the given member are also counted and stored in `member_assignment_count` and `member_core_assignment_count`
        :param prefix: prefix for the resulting attribute names, default=''
        :return: the queryset of subscriptions with annotations `assignment_count` and `core_assignment_count`
        """
        assignments_of_memberships_in_range = functools.partial(
            When,
            Q(subscriptionmembership__leave_date__isnull=True) |
            Q(subscriptionmembership__leave_date__gte=F('subscriptionmembership__member__assignment__job__time__date')),
            subscriptionmembership__join_date__lte=F('subscriptionmembership__member__assignment__job__time__date'),
            subscriptionmembership__member__assignment__job__time__date__gte=start,
            subscriptionmembership__member__assignment__job__time__date__lte=end,
            then='subscriptionmembership__member__assignment__amount'
        )
        default = dict(default=0, output_field=FloatField())
        qs = self
        if of_member:
            qs = qs.annotate(**{
                prefix + 'member_assignment_count': Sum(Case(assignments_of_memberships_in_range(subscriptionmembership__member=of_member), **default), distinct=True),
                prefix + 'member_core_assignment_count': Sum(Case(assignments_of_memberships_in_range(
                    subscriptionmembership__member=of_member,
                    subscriptionmembership__member__assignment__core_cache=True
                ), **default), distinct=True)
            })
        return qs.annotate(**{  # annotate the final results
            prefix + 'assignment_count': Sum(Case(assignments_of_memberships_in_range(), **default), distinct=True),
            prefix + 'core_assignment_count': Sum(Case(assignments_of_memberships_in_range(subscriptionmembership__member__assignment__core_cache=True), **default), distinct=True)
        })

    @method_decorator(default_to_business_year)
    def annotate_required_assignments(self, start=None, end=None):
        """
        calculate the required number of (core) assignments of the subscription given the parts in it, discounted with their duration within the period of interest.
        :param start: beginning of period of interest, default: start of current business year
        :param end: end of period of interest, default: end of current business year
        :return: the queryset of subscriptions with annotations `required_assignments` and `required_core_assignments`
        """
        return self.alias(
            # convert trial days into duration. Minus 1 to end up at the end of the last trial day, e.g., 1. + 30 days = 30. (not 31.)
            # Note: if `microseconds_in_day` was float, the addition with activation date later would fail on sqlite
            parts__type__trial_duration=ExpressionWrapper(F('parts__type__trial_days') * self.microseconds_in_day - 1, DurationField()),
            # find (assumed) deactivation date of part
            parts__forecast_final_date=Least(
                Case(
                    # use deactivation date if set
                    When(parts__deactivation_date__isnull=False,
                         then='parts__deactivation_date'),
                    # on trial subs without deactivation date assume they will last for trial duration.
                    When(parts__type__trial_days__gt=0,
                         then=F('parts__activation_date') + F('parts__type__trial_duration')),
                    # otherwise default to end of period
                    default=end,
                    output_field=DateField()
                ),
                # limit final date to period of interest
                end
            ),
            parts__duration_multiplier=Greatest(
                # number of days subscription part is actually active within period of interest. Add a day because activation day should also count to duration
                F('parts__forecast_final_date') - Greatest('parts__activation_date', start) + datetime.timedelta(1),
                # ignore values <0 resulting from parts outside the period of interest
                0.0,
                output_field=FloatField()
            )
            # divided by number of days within which the assignments are required
            / Case(
                When(parts__type__trial_days__gt=0,
                     then='parts__type__trial_days'),
                default=365,  # ignore leap years
                output_field=FloatField()
            )
            / float(self.microseconds_in_day),
            parts__required_assignments_discount=Case(
                # ignore parts that have not startet yet
                When(parts__activation_date__isnull=True,
                     then=0.0),
                # get discount ratio for required assignments
                default='parts__duration_multiplier'
            )
        ).annotate(  # annotate the final results
            required_assignments=Round(Sum(F('parts__type__required_assignments') * F('parts__required_assignments_discount'), distinct=True, default=0.0)),
            required_core_assignments=Round(Sum(F('parts__type__required_core_assignments') * F('parts__required_assignments_discount'), distinct=True, default=0.0)),
        )

    def annotate_assignments_progress(self, prefix=''):
        """
        Calculate progress, i.e. percentage of done vs. required assignments
        can only be applied in combination with `annotate_required_assignments` and `annotate_assignment_counts`
        :param prefix: prefix to be used on the `assignment_count` and `core_assignment_count`. Use it to match the prefix applied with `annotate_assignment_counts`. default=''
        :return: the queryset of subscriptions with annotations `assignments_progress` and `core_assignments_progress`
        """
        return self.annotate(**{
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

    @method_decorator(default_to_business_year)
    def annotate_assignments(self, start=None, end=None, of_member=None, count_jobs_until=None):
        """
        annotate required and made assignments and calculated progress for core and in general
        count_jobs_until: only account for jobs until this date
        :param start: beginning of period of interest, default: start of current business year
        :param end: end of period of interest, default: end of current business year
        :param of_member: if set, assignments of the given member are also counted and stored in `member_assignment_count` and `member_core_assignment_count`
        :param count_jobs_until: if set, `annotate_assignment_counts` will only count until this date instead of end
        :return: the queryset of subscriptions with annotations `assignment_count`, `core_assignment_count`, `required_assignments`, `required_core_assignments`,
        `assignments_progress` and `core_assignments_progress`
        """
        return self.annotate_assignment_counts(start, count_jobs_until or end, of_member).\
            annotate_required_assignments(start, end).annotate_assignments_progress()
