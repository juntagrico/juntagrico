# -*- coding: utf-8 -*-

from juntagrico.models import *

class ExtraSubscriptionCategoryDao:
    def __init__(self):
        pass

    @staticmethod
    def all_categories_ordered():
        return ExtraSubscriptionCategory.objects.all().order_by("sort_order")
