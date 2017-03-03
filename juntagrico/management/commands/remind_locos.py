from django.core.management.base import BaseCommand, CommandError

from juntagrico.models import *
from django.utils import timezone
import datetime
from juntagrico.mailer import send_job_reminder
from django.utils import timezone


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):

        now = timezone.now()
        end = now + datetime.timedelta(days=2)
        for job in Job.objects.filter(time__range=(now, end), reminder_sent__exact=False):
            participants = []
            emails = []
            for bohne in Assignment.objects.filter(job_id=job.id):
                if bohne.loco is not None:
                    participants.append(str(bohne.loco))
                    emails.append(bohne.loco.email)
            send_job_reminder(emails, job, ", ".join(participants), "www.ortoloco.ch")
            job.reminder_sent = True
            job.save()
            print("reminder sent for job " + str(job.id))


