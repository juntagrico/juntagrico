# -*- coding: utf-8 -*-

import juntagrico

class ExtraSubscriptionCategoryDao:
    def __init__(self):
        pass

    @staticmethod
    def all_categories_ordered():
        return juntagrico.models.ExtraSubscriptionCategory.objects.all().order_by("sort_order")
