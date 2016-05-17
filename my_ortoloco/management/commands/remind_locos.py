from django.core.management.base import BaseCommand, CommandError

from my_ortoloco.models import *
from django.utils import timezone
import datetime
from my_ortoloco.mailer import send_job_reminder


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):

        


