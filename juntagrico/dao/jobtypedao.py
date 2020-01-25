from juntagrico.entity.jobs import JobType


class JobTypeDao:

    @staticmethod
    def types_by_coordinator(member):
        return JobType.objects.filter(activityarea__coordinator=member)

    @staticmethod
    def visible_types_by_coordinator(member):
        return JobType.objects.filter(activityarea__coordinator=member).filter(visible=True)

    @staticmethod
    def visible_types():
        return JobType.objects.filter(visible=True)

    @staticmethod
    def types_by_area(area_id):
        return JobType.objects.all().filter(activityarea=area_id)
