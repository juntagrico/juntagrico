from django_cron import cronScheduler, Job
import models
from django.utils import timezone
import datetime
from mailer import send_job_reminder


class Send_Job_Reminders(Job):
    run_every = 60 # every minute, but the cron library does it every 10minutes so it gets executed between 10 and 11 minutes

    def job(self):
        for job in models.Job.objects.all():
            needs_reminder = job.time - datetime.timedelta(1) < datetime.datetime.now()
            is_past = job.time < datetime.datetime.now()
            if not job.reminder_sent and needs_reminder and not is_past:
                participants = []
                emails = []
                for bohne in models.Boehnli.objects.filter(job_id=job.id):
                    if bohne.loco is not None:
                        participants.append(str(bohne.loco))
                        emails.append(bohne.loco.email)
                send_job_reminder(emails, job, ", ".join(participants), "http://my.ortoloco.ch")
                job.reminder_sent = True
                job.save()



cronScheduler.register(Send_Job_Reminders)

