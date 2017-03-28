# -*- coding: utf-8 -*-

import juntagrico


class AssignmentDao:
    def __init__(self):
        pass

    @staticmethod
    def assignments_for_job(job_identifier):
        return juntagrico.models.Assignment.objects.filter(job_id=job_identifier)


    @staticmethod
    def assignments_for_job_and_member(job_identifier, member):
        return juntagrico.models.Assignment.objects.filter(job_id=job_identifier).filter(member=member)

    @staticmethod
    def assignments_for_member(member):
        return juntagrico.models.Assignment.objects.filter(member=member)
