# -*- coding: utf-8 -*-

import juntagrico

class AssignmentDao:

    @staticmethod
    def assignments_for_job(job_identifier):
        return  juntagrico.models.Assignment.objects.filter(job_id=job_identifier)

    @staticmethod
    def assignments_for_member(member):
        return  juntagrico.models.Assignment.objects.filter(member=member)
