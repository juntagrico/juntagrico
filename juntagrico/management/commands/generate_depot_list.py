import datetime

from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from juntagrico.config import Config
from juntagrico.entity.subs import Subscription
from juntagrico.signals import called
from juntagrico.util.depot_list import depot_list_data


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
    def handle(self, *args, force=False, future=False, no_future=False, days=0, **options):
        weekday = datetime.date.today().weekday()
        if not force and weekday not in Config.depot_list_generation_days():
            self.stderr.write('Not the specified day for depot list generation. Use --force to override.')
            return

        if not no_future or future:
            if not future:
                self.stderr.write(
                    'DEPRECATION WARNING: Running depot list generation without --future flag will change behaviour in an upcoming release. '
                    'See release notes of Juntagrico version 1.6.0. Run this command with --future or with --no-future to remove this warning.'
                )
            if future or weekday in Config.depot_list_generation_days():
                Subscription.objects.activate_future_depots()
            else:
                self.stdout.write('Future depots ignored. Use --future to override.')

        for generator in Config.default_depot_list_generators():
            gen = import_string(generator)
            gen(depot_list_data(days))

        called.send(Command)
