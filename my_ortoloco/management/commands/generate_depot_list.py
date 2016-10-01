from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings

from my_ortoloco.models import *
from my_ortoloco.helpers import *
from my_ortoloco.mailer import *

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
        if not options['force'] and timezone.now().weekday()!=settings.DEPOT_LIST_GENERATION_DAY:
            print "not the specified day for depot list generation, use --force to override"
            return
        
        if options['future'] or timezone.now().weekday()==settings.DEPOT_LIST_GENERATION_DAY:
            future_abos = Abo.objects.exclude(future_depot__isnull=True)
            for abo in future_abos:
                abo.depot=abo.future_depot
                abo.future_depot=None
                abo.save()
                send_depot_changed([abo.primary_loco.email],abo.depot,"www.ortoloco.ch")
        
        if options['force'] and not options['future']:
            print "future depots ignored, use --future to override"
        
        depots = Depot.objects.all().order_by("code")

        categories = []
        types =[]
        for category in ExtraAboCategory.objects.all().order_by("sort_order"):
                cat={}
                cat["name"]= category.name
                cat["description"] = category.description
                count = 0
                for extra_abo in ExtraAboType.objects.all().filter(category = category).order_by("sort_order"):
                    count+=1
                    type={}
                    type["name"] = extra_abo.name
                    type["size"] = extra_abo.size
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
            depot.fill_active_abo_cache()
            row = overview.get(depot.get_weekday_display())
            count=0
            while count < len(row):
                row[count] += depot.overview_cache[count]
                all[count] += depot.overview_cache[count]
                count+=1; 
            
        overview["Dienstag"].insert(2, overview["Dienstag"][0]+2*overview["Dienstag"][1])
        overview["Donnerstag"].insert(2, overview["Donnerstag"][0]+2*overview["Donnerstag"][1])
        overview["all"].insert(2, overview["all"][0]+2*overview["all"][1])
            
        renderdict = {
            "overview": overview,
            "depots": depots,
            "categories" : categories,
            "types" : types,
            "datum": timezone.now(),
            "cover_sheets": settings.DEPOT_LIST_COVER_SHEETS,
            "depot_overviews": settings.DEPOT_LIST_OVERVIEWS,
        }

        render_to_pdf_storage( "exports/all_depots.html", renderdict, 'dpl.pdf')


