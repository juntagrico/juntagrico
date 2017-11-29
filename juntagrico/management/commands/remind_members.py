from django.core.management.base import BaseCommand

from juntagrico.models import *
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.dao.jobdao import JobDao


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):

        now = timezone.now()
        end = now + datetime.timedelta(days=2)
        for job in JobDao.jobs_to_remind(now, end):
            participants = []
            emails = []
            for assignment in AssignmentDao.assignments_for_job(job.id):
                if assignment.member is not None:
                    participants.append(str(assignment.member))
                    emails.append(assignment.member.email)
            send_job_reminder(emails, job, ', '.join(participants))
            job.reminder_sent = True
            job.save()
            print(('reminder sent for job ' + str(job.id)))
