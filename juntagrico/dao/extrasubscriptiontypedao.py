# -*- coding: utf-8 -*-

from juntagrico.models import ExtraSubscriptionType

class ExtraSubscriptionTypeDao:

    @staticmethod
    def all_extra_types():
        return ExtraSubscriptionType.objects.all()

    @staticmethod
    def extra_types_by_category_ordered():
        return ExtraSubscriptionType.objects.all().filter(category=category).order_by("sort_order")

