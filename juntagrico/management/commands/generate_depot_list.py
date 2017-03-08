from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings

from juntagrico.models import *
from juntagrico.helpers import *
from juntagrico.mailer import *
from juntagrico.config import *

import datetime


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
        if not options['force'] and timezone.now().weekday()!=settings.DEPOT_LIST_GENERAboTION_DAboY:
            print "not the specified day for depot list generation, use --force to override"
            return
        
        if options['future'] or timezone.now().weekday()==settings.DEPOT_LIST_GENERAboTION_DAboY:
            future_subscriptions = Subscription.objects.exclude(future_depot__isnull=True)
            for subscription in future_subscriptions:
                subscription.depot=subscription.future_depot
                subscription.future_depot=None
                subscription.save()
                emails = []
                for member in subscription.recipients():
                    emails.append(member.email)
                send_depot_changed(emails,subscription.depot,Config.server_url())
        
        if options['force'] and not options['future']:
            print "future depots ignored, use --future to override"
        Subscription.fill_sizes_cache()
        
        depots = Depot.objects.all().order_by("code")
        
        subscription_names = []
        for subscription_size in SubscriptionSize.objects.filter(depot_list=True).order_by('size'):
            subscription_names.append(subscription_size.name)
        
        categories = []
        types =[]
        for category in ExtraSubscriptionCategory.objects.all().order_by("sort_order"):
                cat={}
                cat["name"]= category.name
                cat["description"] = category.description
                count = 0
                for extra_subscription in ExtraSubscriptionType.objects.all().filter(category = category).order_by("sort_order"):
                    count+=1
                    type={}
                    type["name"] = extra_subscription.name
                    type["size"] = extra_subscription.size
                    type["last"]=False
                    types.append(type)
                type["last"]=True
                cat["count"] = count
                categories.append(cat)    

        overview = {
            'Dienstag': None,
            'Donnerstag': None,
            'all': None
        }

        count = len(types)+2
        overview["Dienstag"] = [0]*count
        overview["Donnerstag"] = [0]*count
        overview["all"] = [0]*count
            
        all = overview.get('all')

        for depot in depots:
            depot.fill_overview_cache()
            depot.fill_active_subscription_cache()
            row = overview.get(depot.get_weekday_display())
            count=0
            while count < len(row):
                row[count] += depot.overview_cache[count]
                all[count] += depot.overview_cache[count]
                count+=1; 
        
        insert_point = len(subscription_names)
        overview["Dienstag"].insert(insert_point, 0)
        overview["Donnerstag"].insert(insert_point, 0)
        overview["all"].insert(insert_point, 0)
        
        index=0
        for subscription_size in SubscriptionSize.objects.filter(depot_list=True).order_by('size'):
            overview["Dienstag"][insert_point]=overview["Dienstag"][insert_point]+ subscription_size.size*overview["Dienstag"][index]
            overview["Donnerstag"][insert_point]=overview["Donnerstag"][insert_point]+ subscription_size.size*overview["Donnerstag"][index]
            overview["all"][insert_point]=overview["all"][insert_point]+ subscription_size.size*overview["all"][index]
            index+=1
            
        renderdict = {
            "overview": overview,
            "depots": depots,
            "subscription_names": subscription_names,
            "categories" : categories,
            "types" : types,
            "datum": timezone.now(),
            "cover_sheets": settings.DEPOT_LIST_COVER_SHEETS,
            "depot_overviews": settings.DEPOT_LIST_OVERVIEWS,
        }

        render_to_pdf_storage( "exports/all_depots.html", renderdict, 'dpl.pdf')


