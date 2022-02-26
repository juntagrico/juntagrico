import datetime

from django.db.models import Q, Count, F
from django.utils import timezone
from polymorphic.query import PolymorphicQuerySet
from juntagrico.config import Config


class JobQuerySet(PolymorphicQuerySet):
    def sorted(self):
        return self.order_by('time')

    def next(self, start=None, **kwargs):
        """
        :param start: select future jobs relative to this date or datetime
        :param kwargs: if additional keyword arguments are given they are passed to timedelta
                       that limits the result to a date relative to the start date
        """
        start = start or timezone.now()
        f = 'time__date__gte' if isinstance(start, datetime.date) else 'time__gte'
        qs = self.sorted().filter(**{f: start})
        if kwargs:
            return qs.until(start + datetime.timedelta(**kwargs))
        return qs

    def until(self, date):
        f = 'time__date__lte' if isinstance(date, datetime.date) else 'time__lte'
        return self.filter(**{f: date})

    def pinned(self):
        return self.filter(pinned=True)

    def promoted(self):
        return self.filter(RecuringJob___type__name__in=Config.promoted_job_types())[:Config.promomted_jobs_amount()]

    def to_remind(self):
        return self.filter(reminder_sent__exact=False)

    def with_free_slots(self):
        return self.annotate_occupied_slots().filter(Q(infinite_slots=True) | Q(occupied_count__lt=F('slots')))

    def annotate_occupied_slots(self):
        return self.annotate(occupied_count=Count('assignments'))

    def in_area(self, area):
        return self.filter(
            Q(RecuringJob___type__activityarea=area) | Q(
                OneTimeJob___activityarea=area))

    def of_member(self, member):
        return self.filter(assignments__member=member).distinct()

    def of_coordinator(self, member):
        return self.filter(
            Q(RecuringJob___type__activityarea__coordinator=member) | Q(
                OneTimeJob___activityarea__coordinator=member))
