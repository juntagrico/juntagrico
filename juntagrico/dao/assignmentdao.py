from django.utils import timezone

import juntagrico


class AssignmentDao:

    @staticmethod
    def assignments_for_job(job_identifier):
        return juntagrico.entity.jobs.Assignment.objects.filter(job_id=job_identifier)
