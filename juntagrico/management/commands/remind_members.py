from django.core.management.base import BaseCommand

from juntagrico.entity.jobs import Job
from juntagrico.mailer import membernotification


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):
        for job in Job.objects.next(days=2).to_remind():
            membernotification.job_reminder(job.participant_emails, job)
            job.reminder_sent = True
            job.save()
            print(('reminder sent for job ' + str(job.id)))
