from django.core.management.base import BaseCommand
from django.utils import timezone

from juntagrico.config import Config
from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.extrasubscriptioncategorydao import ExtraSubscriptionCategoryDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.util.pdf import render_to_pdf_storage
from juntagrico.util.temporal import weekdays
from juntagrico.util.subs import activate_future_depots


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
            activate_future_depots()

        if options['force'] and not options['future']:
            print('future depots ignored, use --future to override')

        depot_dict = {
            'subscriptions': SubscriptionDao.all_active_subscritions(),
            'products': SubscriptionProductDao.get_all_for_depot_list(),
            'extra_sub_categories': ExtraSubscriptionCategoryDao.categories_for_depot_list_ordered(),
            'depots': DepotDao.all_depots_order_by_code(),
            'weekdays': {weekdays[weekday['weekday']]: weekday['weekday'] for weekday in
                         DepotDao.distinct_weekdays()},
            'messages': ListMessageDao.all_active()
        }

        render_to_pdf_storage('exports/depotlist.html',
                              depot_dict, 'depotlist.pdf')
        render_to_pdf_storage('exports/depot_overview.html',
                              depot_dict, 'depot_overview.pdf')
        render_to_pdf_storage('exports/amount_overview.html',
                              depot_dict, 'amount_overview.pdf')
