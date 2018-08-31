from django.core.management.base import BaseCommand


from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.extrasubscriptiontypedao import ExtraSubscriptionTypeDao
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao
from juntagrico.dao.extrasubscriptioncategorydao import ExtraSubscriptionCategoryDao
from juntagrico.models import *
from juntagrico.util.pdf import render_to_pdf_storage
from juntagrico.util.temporal import weekdays


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
                send_depot_changed(emails, subscription.depot)

        if options['force'] and not options['future']:
            print('future depots ignored, use --future to override')

        depots = DepotDao.all_depots_order_by_code()

        subscription_names = []
        for subscription_size in SubscriptionSizeDao.sizes_for_depot_list():
            subscription_names.append(subscription_size.name)

        categories = []
        types = []
        for category in ExtraSubscriptionCategoryDao.all_categories_ordered():
            cat = {'name': category.name, 'description': category.description}
            count = 0
            for extra_subscription in ExtraSubscriptionTypeDao.extra_types_by_category_ordered(category):
                count += 1
                es_type = {'name': extra_subscription.name,
                           'size': extra_subscription.size, 'last': False}
                types.append(es_type)
            es_type['last'] = True
            cat['count'] = count
            categories.append(cat)

        used_weekdays = []
        for item in DepotDao.distinct_weekdays():
            used_weekdays.append(weekdays[item['weekday']])

        overview = {
            'all': None
        }
        for weekday in used_weekdays:
            overview[weekday] = None

        count = len(types) + len(subscription_names)
        for weekday in used_weekdays:
            overview[weekday] = [0] * count
        overview['all'] = [0] * count

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
        for weekday in used_weekdays:
            overview[weekday].insert(insert_point, 0)
        overview['all'].insert(insert_point, 0)

        index = 0
        for subscription_size in SubscriptionSizeDao.sizes_for_depot_list():
            for weekday in used_weekdays:
                overview[weekday][insert_point] = overview[weekday][insert_point] + subscription_size.units * \
                    overview[weekday][index]
            overview['all'][insert_point] = overview['all'][insert_point] + subscription_size.units * overview['all'][
                index]
            index += 1

        renderdict = {
            'overview': overview,
            'depots': depots,
            'subscription_names': subscription_names,
            'subscriptioncount': len(subscription_names)+1,
            'categories': categories,
            'types': types,
            'datum': timezone.now(),
            'weekdays': used_weekdays,
            'messages': ListMessageDao.all_active()
        }

        render_to_pdf_storage('exports/legacy.html', renderdict, 'dpl.pdf')
        render_to_pdf_storage('exports/depotlist.html',
                              renderdict, 'depotlist.pdf')
        render_to_pdf_storage('exports/depot_overview.html',
                              renderdict, 'depot_overview.pdf')
        render_to_pdf_storage('exports/amount_overview.html',
                              renderdict, 'amount_overview.pdf')
