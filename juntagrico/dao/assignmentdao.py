from datetime import datetime, time

from django.utils import timezone
from django.utils.timezone import get_default_timezone as gdtz

import juntagrico
from juntagrico.util.temporal import start_of_business_year


class AssignmentDao:

    @staticmethod
    def assignments_for_job(job_identifier):
        return juntagrico.entity.jobs.Assignment.objects.filter(job_id=job_identifier)

    @staticmethod
    def assignments_for_job_and_member(job_identifier, member):
        return juntagrico.entity.jobs.Assignment.objects.filter(job_id=job_identifier).filter(member=member)

    @staticmethod
    def assignments_for_member(member):
        return juntagrico.entity.jobs.Assignment.objects.filter(member=member)

    @staticmethod
    def assignments_for_member_current_business_year(member):
        start = gdtz().localize(datetime.combine(start_of_business_year(), time.min))
        return juntagrico.entity.jobs.Assignment.objects.filter(member=member).\
            filter(job__time__gte=start, job__time__lt=timezone.now())

    @staticmethod
    def upcomming_assignments_for_member(member):
        return juntagrico.entity.jobs.Assignment.objects.filter(member=member).filter(job__time__gte=timezone.now())
