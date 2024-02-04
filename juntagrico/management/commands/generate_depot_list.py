from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from juntagrico.config import Config


class Command(BaseCommand):
    help = ("Generates all depot lists. "
            "If custom DEFAULT_DEPOTLIST_GENERATORS are set, the arguments may have different effects.")

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='force generation of depot list regardless of DEPOT_LIST_GENERATION_DAYS setting',
        )

        parser.add_argument(
            '--future',
            action='store_true',
            dest='future',
            default=False,
            help='apply all pending depot changes, i.e., members wanting to change the depot, before generation, '
                 'regardless of DEPOT_LIST_GENERATION_DAYS setting',
        )

        parser.add_argument(
            '--no-future',
            action='store_true',
            dest='no_future',
            default=False,
            help='prevent automatic depot changes even on weekdays specified in DEPOT_LIST_GENERATION_DAYS. '
                 'Ignored if --future is set',
        )

        parser.add_argument(
            '--days',
            default=0,
            type=int,
            help='produce lists for subscriptions that will be active on the date this number of days in the future. '
                 'This is useful to account for subscriptions with future activation dates. '
                 'Use negative values for past dates.',
        )

    # entry point used by manage.py
    def handle(self, *args, **options):
        for generator in Config.default_depot_list_generators():
            gen = import_string(generator)
            gen(*args, **options)
