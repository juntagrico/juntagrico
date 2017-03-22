from django.core.management.base import BaseCommand

from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.extrasubscriptiontypedao import ExtraSubscriptionTypeDao
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao
from juntagrico.dao.extrasubscriptioncategorydao import ExtraSubscriptionCategory
from juntagrico.models import *


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
        if not options['force'] and timezone.now().weekday() != settings.DEPOT_LIST_GENERATION_DAY:
            print "not the specified day for depot list generation, use --force to override"
            return

        if options['future'] or timezone.now().weekday() == settings.DEPOT_LIST_GENERATION_DAY:
            for subscription in SubscriptionDao.subscritions_with_future_depots():
                subscription.depot = subscription.future_depot
                subscription.future_depot = None
                subscription.save()
                emails = []
                for member in subscription.recipients():
                    emails.append(member.email)
                send_depot_changed(emails, subscription.depot, Config.server_url())

        if options['force'] and not options['future']:
            print "future depots ignored, use --future to override"
        Subscription.fill_sizes_cache()

        depots = DepotDao.all_depots_order_by_code()

        subscription_names = []
        for subscription_size in SubscriptionSizeDao.sizes_for_depot_list():
            subscription_names.append(subscription_size.name)

        categories = []
        types = []
        for category in ExtraSubscriptionCategoryDao.all_categories_ordered():
            cat = {"name": category.name, "description": category.description}
            count = 0
            for extra_subscription in ExtraSubscriptionTypeDao.extra_types_by_category_ordered():
                count += 1
                type = {"name": extra_subscription.name, "size": extra_subscription.size, "last": False}
                types.append(type)
            type["last"] = True
            cat["count"] = count
            categories.append(cat)

        overview = {
            'Dienstag': None,
            'Donnerstag': None,
            'all': None
        }

        count = len(types) + 2
        overview["Dienstag"] = [0] * count
        overview["Donnerstag"] = [0] * count
        overview["all"] = [0] * count

        all = overview.get('all')

        for depot in depots:
            depot.fill_overview_cache()
            depot.fill_active_subscription_cache()
            row = overview.get(depot.get_weekday_display())
            count = 0
            # noinspection PyTypeChecker
            while count < len(row):
                row[count] += depot.overview_cache[count]
                all[count] += depot.overview_cache[count]
                count += 1

        insert_point = len(subscription_names)
        overview["Dienstag"].insert(insert_point, 0)
        overview["Donnerstag"].insert(insert_point, 0)
        overview["all"].insert(insert_point, 0)

        index = 0
        for subscription_size in SubscriptionSizeDao.sizes_for_depot_list():
            overview["Dienstag"][insert_point] = overview["Dienstag"][insert_point] + subscription_size.size * \
                                                                                      overview["Dienstag"][index]
            overview["Donnerstag"][insert_point] = overview["Donnerstag"][insert_point] + subscription_size.size * \
                                                                                          overview["Donnerstag"][index]
            overview["all"][insert_point] = overview["all"][insert_point] + subscription_size.size * overview["all"][
                index]
            index += 1

        renderdict = {
            "overview": overview,
            "depots": depots,
            "subscription_names": subscription_names,
            "categories": categories,
            "types": types,
            "datum": timezone.now(),
            "cover_sheets": settings.DEPOT_LIST_COVER_SHEETS,
            "depot_overviews": settings.DEPOT_LIST_OVERVIEWS,
        }

        render_to_pdf_storage("exports/all_depots.html", renderdict, 'dpl.pdf')
