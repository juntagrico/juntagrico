from django.core.management.base import BaseCommand, CommandError

from my_ortoloco.models import *
from my_ortoloco.model_audit import *

from django.contrib.auth.models import *


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):

        


