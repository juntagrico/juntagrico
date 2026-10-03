import juntagrico


class AssignmentDao:

    @staticmethod
    def assignments_for_job(job_identifier):
        print('AssignmentDao.assignments_for_job is deprecated: Use job.assignment_set.all() instead')
        return juntagrico.entity.jobs.Assignment.objects.filter(job_id=job_identifier)
