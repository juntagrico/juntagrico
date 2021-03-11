import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from juntagrico.dao.jobdao import JobDao
from juntagrico.mailer import membernotification


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):
        now = timezone.now()
        end = now + datetime.timedelta(days=2)
        for job in JobDao.jobs_to_remind(now, end):
            membernotification.job_reminder(job.participant_emails, job)
            job.reminder_sent = True
            job.save()
            print(('reminder sent for job ' + str(job.id)))
