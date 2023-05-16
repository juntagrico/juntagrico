from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from juntagrico.config import Config


class Command(BaseCommand):
    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='force generation of depot list',
        )

        parser.add_argument(
            '--future',
            action='store_true',
            dest='future',
            default=False,
            help='when forced do not ignore future depots',
        )

        parser.add_argument(
            '--days',
            default=0,
            type=int,
            help='produce lists for subscriptions that will be active this number of days in the future',
        )

    # entry point used by manage.py
    def handle(self, *args, **options):
        for generator in Config.default_depot_list_generators():
            gen = import_string(generator)
            gen(*args, **options)
