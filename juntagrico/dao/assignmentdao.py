import juntagrico


class AssignmentDao:

    @staticmethod
    def assignments_for_job(job_identifier):
        print('AssignmentDao.assignments_for_job is DEPRECATED. Use job.assignment_set instead.')
        return juntagrico.entity.jobs.Assignment.objects.filter(job_id=job_identifier)
