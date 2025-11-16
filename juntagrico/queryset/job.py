from datetime import timedelta

from django.db.models import Q, QuerySet
from django.utils import timezone
from polymorphic.query import PolymorphicQuerySet


def q_job_type_search(relations, search_value):
    q = Q()
    for relation in relations:
        q |= Q(**{f'RecuringJob___type__{relation}__icontains': search_value})
        q |= Q(**{f'OneTimeJob___{relation}__icontains': search_value})
    return q


class JobQueryset(PolymorphicQuerySet):
    name_fields = ['displayed_name', 'name']
    location_fields = ['location__name', 'location__addr_street', 'location__addr_zipcode', 'location__addr_location']
    area_fields = ['activityarea__name']
    description_fields = ['description']

    def search_name(self, search_value):
        return self.filter(q_job_type_search(self.name_fields, search_value))

    def search_time(self, search_value):
        # This will search on the ISO string of the datetime, which is better than nothing
        return self.filter(time__icontains=search_value)

    def search_location(self, search_value):
        return self.filter(q_job_type_search(self.location_fields, search_value))

    def search_area(self, search_value):
        return self.filter(q_job_type_search(self.area_fields, search_value))

    def full_text_search(self, search_value):
        return self.filter(
            q_job_type_search(
                self.name_fields + self.location_fields + self.area_fields + self.description_fields,
                search_value
            ) | Q(time__icontains=search_value)
        )

    def order_by_recent(self, days=7):
        cutoff = timezone.now() - timedelta(days=days)
        return self.annotate(is_old=Q(time__lt=cutoff)).order_by('is_old', 'time')


class AssignmentQuerySet(QuerySet):
    def by_areas(self, areas):
        from juntagrico.entity.jobs import Job
        return self.filter(
            job__in=Job.objects.filter(
                Q(OneTimeJob___activityarea__in=areas) |
                Q(RecuringJob___type__activityarea__in=areas)
            )
        )
