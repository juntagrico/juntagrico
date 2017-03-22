# -*- coding: utf-8 -*-

from juntagrico.models import *

class AssignmentDao:

    @staticmethod
    def assignments_for_job(job_identifier):
        return  Assignment.objects.filter(job_id=job_identifier)

    @staticmethod
    def assignments_for_member(member):
        return  Assignment.objects.filter(member=member)
