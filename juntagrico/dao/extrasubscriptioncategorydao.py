# -*- coding: utf-8 -*-

from juntagrico.models import ExtraSubscriptionCategory

class ExtraSubscriptionCategoryDao:
    def __init__(self):
        pass

    @staticmethod
    def all_categories_ordered():
        return ExtraSubscriptionCategory.objects.all().order_by("sort_order")
