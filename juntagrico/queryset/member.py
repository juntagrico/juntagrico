from django.db.models import QuerySet, Sum, Case, When
from django.utils.decorators import method_decorator

from juntagrico.util.temporal import default_to_business_year


class MemberQuerySet(QuerySet):

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
