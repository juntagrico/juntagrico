from django.core.management.base import BaseCommand, CommandError

from my_ortoloco.models import *
from django.utils import timezone
import datetime
from my_ortoloco.mailer import send_job_reminder


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):

        now = datetime.datetime.now()
        end = now + datetime.timedelta(days=1)
        for job in Job.objects.filter(time__range=(now, end), reminder_sent__exact=False):
            participants = []
            emails = []
            for bohne in Boehnli.objects.filter(job_id=job.id):
                if bohne.loco is not None:
                    participants.append(str(bohne.loco))
                    emails.append(bohne.loco.email)
            send_job_reminder(emails, job, ", ".join(participants), "http://my.ortoloco.ch")
            job.reminder_sent = True
            job.save()
            print("reminder sent for job " + str(job.id))


