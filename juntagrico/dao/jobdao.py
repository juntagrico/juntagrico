# -*- coding: utf-8 -*-

from juntagrico.models import RecuringJob, OneTimeJob, Job


class JobDao:
    def __init__(self):
        pass

    @staticmethod
    def recuring_by_type(type_id):
        return RecuringJob.objects.filter(typeid=type_id)

    @staticmethod
    def ids_for_area_by_contact(member):
        otjidlist = list(
            OneTimeJob.objects.filter(activityarea__coordinator=member).values_list('id', flat=True))
        rjidlist = list(
            RecuringJob.objects.filter(type_activityarea__coordinator=member).values_list('id',
                                                                                          flat=True))
        return otjidlist + rjidlist

    @staticmethod
    def jobs_by_ids(jidlist):
        return Job.objects.filter(id__in=jidlist)

    @staticmethod
    def jobs_to_remind(now, end):
        return Job.objects.filter(time__range=(now, end), reminder_sent__exact=False)




