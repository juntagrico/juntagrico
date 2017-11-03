# -*- coding: utf-8 -*-

from juntagrico.models import *


class DepotDao:

    @staticmethod
    def all_depots():
        return Depot.objects.all()

    @staticmethod
    def all_depots_order_by_code():
        return Depot.objects.all().order_by('code')

    @staticmethod
    def depots_for_contact(member):
        return Depot.objects.filter(contact=member)

    @staticmethod
    def depot_by_id(identifier):
        return Depot.objects.all().filter(id=identifier)[0]

    @staticmethod
    def distinct_weekdays():
        return Depot.objects.all().order_by('weekday').values('weekday').distinct()
