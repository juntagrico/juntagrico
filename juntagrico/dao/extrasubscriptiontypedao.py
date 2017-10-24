# -*- coding: utf-8 -*-
import juntagrico


class ExtraSubscriptionTypeDao:

    @staticmethod
    def all_extra_types():
        return juntagrico.models.ExtraSubscriptionType.objects.all()

    @staticmethod
    def extra_types_by_category_ordered(category):
        return juntagrico.models.ExtraSubscriptionType.objects.all().filter(category=category).order_by('sort_order')
