import juntagrico
from juntagrico.util.temporal import *

class AssignmentDao:

    @staticmethod
    def assignments_for_job(job_identifier):
        return juntagrico.models.Assignment.objects.filter(job_id=job_identifier)


    @staticmethod
    def assignments_for_job_and_member(job_identifier, member):
        return juntagrico.models.Assignment.objects.filter(job_id=job_identifier).filter(member=member)

    @staticmethod
    def assignments_for_member(member):
        return juntagrico.models.Assignment.objects.filter(member=member)

    @staticmethod
    def assignments_for_member_current_business_year(member):
        return juntagrico.models.Assignment.objects.filter(member=member).filter(job__time__gte=start_of_business_year(), job__time__lt=timezone.now())
    @staticmethod
    def upcomming_assignments_for_member(member):
        return juntagrico.models.Assignment.objects.filter(member=member).filter(job__time__gte=timezone.now())
