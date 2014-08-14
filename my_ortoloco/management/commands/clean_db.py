from django.core.management.base import BaseCommand, CommandError

from my_ortoloco.models import *
from my_ortoloco.model_audit import *

from django.contrib.auth.models import *


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):

        Abo.objects.all().delete()
        Anteilschein.objects.all().delete()
        Audit.objects.all().delete()
        Depot.objects.all().delete()
        ExtraAboType.objects.all().delete()
        Boehnli.objects.all().delete()

        # delete in correct order to avoid triggering protection
        Job.objects.all().delete()
        JobType.objects.all().delete()
        Taetigkeitsbereich.objects.all().delete()

        # delete all users except super
        Loco.objects.filter(user__id__gt=1).delete()
        User.objects.filter(id__gt=1).delete()

        # auth groups
        Group.objects.all().delete()


