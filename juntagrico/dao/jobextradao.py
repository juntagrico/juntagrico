from juntagrico.entity.jobs import JobExtra


class JobExtraDao:

    @staticmethod
    def all_job_extras():
        return JobExtra.objects.all()

    @staticmethod
    def by_type(type_id):
        return JobExtra.objects.filter(recuring_type__id=type_id)
