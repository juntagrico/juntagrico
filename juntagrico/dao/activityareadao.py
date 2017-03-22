# -*- coding: utf-8 -*-

from juntagrico.models import *

class ActivityAreaDao:
    def __init__(self):
        pass

    @staticmethod
    def all_visible_areas():
        return ActivityArea.objects.filter(hidden=False)

    @staticmethod
    def areas_by_coordinator(member):
        return ActivityArea.objects.filter(coordinator=member)

    @staticmethod
    def all_visible_areas_ordered():
        return ActivityArea.objects.filter(hidden=False).order_by("-core", "name")
