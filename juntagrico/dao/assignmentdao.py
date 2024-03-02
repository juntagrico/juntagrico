from django.utils import timezone

import juntagrico


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
    def upcomming_assignments_for_member(member):
        return juntagrico.entity.jobs.Assignment.objects.filter(member=member).filter(job__time__gte=timezone.now())
