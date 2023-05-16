import datetime

from django.utils import timezone

from juntagrico.config import Config
from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.entity.subs import Subscription
from juntagrico.mailer import adminnotification
from juntagrico.util.pdf import render_to_pdf_storage
from juntagrico.util.subs import activate_future_depots
from juntagrico.util.temporal import weekdays


def default_depot_list_generation(*args, days=0, force=False, future=False, **options):
    if not force and timezone.now().weekday() not in Config.depot_list_generation_days():
        print(
            'not the specified day for depot list generation, use --force to override')
        return

    if future or timezone.now().weekday() in Config.depot_list_generation_days():
        activate_future_depots()

    if force and not future:
        print('future depots ignored, use --future to override')

    date = datetime.date.today() + datetime.timedelta(days)

    depot_dict = {
        'subscriptions': Subscription.objects.active_on(date),
        'products': SubscriptionProductDao.get_all_for_depot_list(),
        'depots': DepotDao.all_depots_for_list(),
        'date': date,
        'weekdays': {weekdays[weekday['weekday']]: weekday['weekday'] for weekday in
                     DepotDao.distinct_weekdays_for_depot_list()},
        'messages': ListMessageDao.all_active()
    }

    render_to_pdf_storage('exports/depotlist.html',
                          depot_dict, 'depotlist.pdf')
    render_to_pdf_storage('exports/depot_overview.html',
                          depot_dict, 'depot_overview.pdf')
    render_to_pdf_storage('exports/amount_overview.html',
                          depot_dict, 'amount_overview.pdf')

    adminnotification.depot_list_generated()
