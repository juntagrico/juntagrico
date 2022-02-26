from django.utils import timezone

from juntagrico.config import Config
from juntagrico.entity.depot import Depot
from juntagrico.entity.listmessage import ListMessage
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import SubscriptionProduct
from juntagrico.mailer import adminnotification
from juntagrico.util.pdf import render_to_pdf_storage
from juntagrico.util.subs import activate_future_depots


def default_depot_list_generation(*args, **options):
    if not options['force'] and timezone.now().weekday() not in Config.depot_list_generation_days():
        print(
            'not the specified day for depot list generation, use --force to override')
        return

    if options['future'] or timezone.now().weekday() in Config.depot_list_generation_days():
        activate_future_depots()

    if options['force'] and not options['future']:
        print('future depots ignored, use --future to override')

    depot_dict = {
        'subscriptions': Subscription.objects.active(),
        'products': SubscriptionProduct.objects.for_depot_list(),
        'depots': Depot.objects.for_depot_list(),
        'messages': ListMessage.objects.filter(active=True)
    }

    render_to_pdf_storage('exports/depotlist.html',
                          depot_dict, 'depotlist.pdf')
    render_to_pdf_storage('exports/depot_overview.html',
                          depot_dict, 'depot_overview.pdf')
    render_to_pdf_storage('exports/amount_overview.html',
                          depot_dict, 'amount_overview.pdf')

    adminnotification.depot_list_generated()
