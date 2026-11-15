import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from juntagrico.entity.jobs import Job
from juntagrico.mailer import membernotification


class Command(BaseCommand):
    help = ("Sends a job reminder email to all members that are signed up to a job in the next 48 hours. "
            "Executing the command twice will NOT send another notification to those already notified. ")

    # entry point used by manage.py
    def handle(self, *args, **options):
        now = timezone.now()
        end = now + datetime.timedelta(days=2)
        for job in Job.objects.filter(time__range=(now, end), reminder_sent=False):
            membernotification.job_reminder(job)
            job.reminder_sent = True
            job.save()
            print(f'reminder sent for job {job.id}')
