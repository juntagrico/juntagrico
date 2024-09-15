import datetime

from django.db.models.functions import Lower

from juntagrico.config import Config
from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.entity.depot import Tour
from juntagrico.entity.subs import Subscription
from juntagrico.mailer import adminnotification
from juntagrico.util.pdf import render_to_pdf_storage


def depot_list_data(days=0):
    date = datetime.date.today() + datetime.timedelta(days)

    return {
        'subscriptions': Subscription.objects.active_on(date).order_by(Lower('primary_member__first_name'),
                                                                       Lower('primary_member__last_name')),
        'products': SubscriptionProductDao.get_all_for_depot_list(),
        'depots': DepotDao.all_depots_for_list(),
        'date': date,
        'tours': Tour.objects.filter(visible_on_list=True),
        'messages': ListMessageDao.all_active()
    }


def default_depot_list_generation(*args, days=0, force=False, future=False, no_future=False, **options):
    weekday = datetime.date.today().weekday()
    if not force and weekday not in Config.depot_list_generation_days():
        print(
            'not the specified day for depot list generation, use --force to override')
        return

    if not no_future or future:
        if not future:
            print('DEPRECATION WARNING: Running depot list generation without --future flag will change behaviour in an upcoming release. '
                  'See release notes of Juntagrico version 1.6.0. Run this command with --future or with --no-future to remove this warning.')
        if future or weekday in Config.depot_list_generation_days():
            Subscription.objects.activate_future_depots()
        else:
            print('future depots ignored, use --future to override')

    depot_dict = depot_list_data(days)

    render_to_pdf_storage('exports/depotlist.html',
                          depot_dict, 'depotlist.pdf')
    render_to_pdf_storage('exports/depot_overview.html',
                          depot_dict, 'depot_overview.pdf')
    render_to_pdf_storage('exports/amount_overview.html',
                          depot_dict, 'amount_overview.pdf')

    adminnotification.depot_list_generated()
