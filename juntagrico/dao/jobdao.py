# -*- coding: utf-8 -*-
from django.utils import timezone

from juntagrico.models import *
from juntagrico.config import Config


class JobDao:
    @staticmethod
    def job_by_id(job_id):
        return Job.objects.filter(id=job_id)[0]

    @staticmethod
    def recurings_by_type(type_id):
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
    def jobs_ordered_by_time():
        return Job.objects.all().order_by('time')

    @staticmethod
    def jobs_to_remind(now, end):
        return Job.objects.filter(time__range=(now, end), reminder_sent__exact=False)

    @staticmethod
    def get_current_jobs():
        return Job.objects.filter(time__gte=timezone.now()).order_by('time')

    @staticmethod
    def get_current_one_time_jobs():
        return OneTimeJob.objects.filter(time__gte=timezone.now()).order_by('time')

    @staticmethod
    def get_current_recuring_jobs():
        return RecuringJob.objects.filter(time__gte=timezone.now()).order_by('time')

    @staticmethod
    def get_pinned_jobs():
        return Job.objects.filter(pinned=True, time__gte=timezone.now())

    @staticmethod
    def get_promoted_jobs():
        return RecuringJob.objects.filter(type__name__in=Config.promoted_job_types(), time__gte=timezone.now()).order_by('time')[:Config.promomted_jobs_amount()]




