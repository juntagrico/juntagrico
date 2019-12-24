from juntagrico.entity.jobs import JobExtra


class JobExtraDao:

    @staticmethod
    def all_job_extras():
        return JobExtra.objects.all()
