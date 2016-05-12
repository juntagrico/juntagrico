import models
from django.utils import timezone
import datetime
from mailer import send_job_reminder
from django_cron import CronJobBase, Schedule

class Send_Job_Reminders(CronJobBase):
    RUN_EVERY_MINS = 1 # every minute, but the cron library does it every 10minutes so it gets executed between 10 and 11 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'my_ortoloco.reminders'    # a unique code
    
    def do(self):
        now = datetime.datetime.now()
        end = now + datetime.timedelta(days=1)
        for job in models.Job.objects.filter(time__range=(now, end), reminder_sent__exact=False):
            participants = []
            emails = []
            for bohne in models.Boehnli.objects.filter(job_id=job.id):
                if bohne.loco is not None:
                    participants.append(str(bohne.loco))
                    emails.append(bohne.loco.email)
            send_job_reminder(emails, job, ", ".join(participants), "http://my.ortoloco.ch")
            job.reminder_sent = True
            job.save()
            print("reminder sent for job " + str(job.id))







