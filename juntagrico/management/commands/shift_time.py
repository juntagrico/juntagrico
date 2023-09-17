from datetime import timedelta, datetime

from django.core.management.base import BaseCommand
from django.db.models import F

from juntagrico.entity.jobs import Job


class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument(
            'hours',
            type=float,
            help='Amount of hours the time should be shifted to the future',
        )

        parser.add_argument(
            '-s', '--start',
            type=datetime.fromisoformat,
            help='Only modify times after this date and time',
        )

        parser.add_argument(
            '-e', '--end',
            type=datetime.fromisoformat,
            help='Only modify times before this date and time',
        )

    def handle(self, hours, *args, start=None, end=None, **options):
        jobs = Job.objects.all()
        if start:
            jobs = jobs.filter(time__gt=start)
        if end:
            jobs = jobs.filter(time__lt=end)
        jobs.update(time=F('time') + timedelta(hours=hours))
