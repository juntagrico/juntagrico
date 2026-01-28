from datetime import datetime, time, date

from django.utils import timezone
from django.utils.timezone import get_default_timezone as gdtz

from juntagrico.entity.jobs import Job, RecuringJob, OneTimeJob


class JobDao:
    @staticmethod
    def jobs_ordered_by_time():
        return Job.objects.all().order_by('time')

    @staticmethod
    def jobs_to_remind(now, end):
        return Job.objects.filter(time__range=(now, end), reminder_sent__exact=False)

    @staticmethod
    def get_jobs_for_current_day():
        daystart = datetime.combine(date.today(), time.min, tzinfo=gdtz())
        return Job.objects.filter(time__gte=daystart).order_by('time')

    @staticmethod
    def get_current_one_time_jobs():
        return OneTimeJob.objects.filter(time__gte=timezone.now()).order_by('time')

    @staticmethod
    def get_current_recuring_jobs():
        return RecuringJob.objects.filter(time__gte=timezone.now()).order_by('time')

    @staticmethod
    def upcoming_jobs_for_member(member):
        return Job.objects \
            .filter(time__gte=timezone.now(), assignment__member=member) \
            .distinct() \
            .order_by('time')
