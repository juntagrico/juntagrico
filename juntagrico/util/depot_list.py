import datetime

from django.db.models.functions import Lower

from juntagrico.config import Config
from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.entity.depot import Tour
from juntagrico.entity.subs import Subscription
from juntagrico.util.pdf import render_to_pdf_storage


def depot_list_data(days=0):
    date = datetime.date.today() + datetime.timedelta(days)
    return {
        'date': date,
        'subscriptions': Subscription.objects.active_on(date).order_by(
            Lower('primary_member__first_name'), Lower('primary_member__last_name')
        ),
        'products': SubscriptionProductDao.get_all_for_depot_list(),
        'depots': DepotDao.all_depots_for_list(),
        'tours': Tour.objects.filter(visible_on_list=True),
        'messages': ListMessageDao.all_active()
    }


def default_depot_list_generation(context):
    for depot_list in Config.depot_lists():
        render_to_pdf_storage(
            depot_list['template'],
            context | depot_list['extra_context'],
            depot_list['file_name'] + '.pdf'
        )
