from django.core.management.base import BaseCommand
from django.utils import timezone

from juntagrico.config import Config
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.mailer import MemberNotification
from juntagrico.util.pdf import render_to_pdf_storage
from juntagrico.util.view_dicts.pdf_lists import get_depotlist_dict, get_depotoverview_dict, get_amountlist_dict


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
        # Named (optional) arguments
        parser.add_argument(
            '--future',
            action='store_true',
            dest='future',
            default=False,
            help='when forced do not ignore future depots',
        )

    # entry point used by manage.py
    def handle(self, *args, **options):
        if not options['force'] and timezone.now().weekday() not in Config.depot_list_generation_days():
            print(
                'not the specified day for depot list generation, use --force to override')
            return

        if options['future'] or timezone.now().weekday() in Config.depot_list_generation_days():
            for subscription in SubscriptionDao.subscritions_with_future_depots():
                subscription.depot = subscription.future_depot
                subscription.future_depot = None
                subscription.save()
                emails = []
                for member in subscription.recipients:
                    emails.append(member.email)
                MemberNotification.depot_changed(emails, subscription.depot)

        if options['force'] and not options['future']:
            print('future depots ignored, use --future to override')

        render_to_pdf_storage('exports/depotlist.html',
                              get_depotlist_dict(), 'depotlist.pdf')
        render_to_pdf_storage('exports/depot_overview.html',
                              get_depotoverview_dict(), 'depot_overview.pdf')
        render_to_pdf_storage('exports/amount_overview.html',
                              get_amountlist_dict(), 'amount_overview.pdf')
