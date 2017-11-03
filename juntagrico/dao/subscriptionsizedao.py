# -*- coding: utf-8 -*-
import juntagrico


class SubscriptionSizeDao:

    @staticmethod
    def sizes_for_depot_list():
        return juntagrico.models.SubscriptionSize.objects.filter(depot_list=True).order_by('size')

    @staticmethod
    def all_sizes_ordered():
        return juntagrico.models.SubscriptionSize.objects.order_by('size')

    @staticmethod
    def sizes_by_size(size):
        return juntagrico.models.SubscriptionSize.objects.filter(size=size)

    @staticmethod
    def sizes_by_name(name):
        return juntagrico.models.SubscriptionSize.objects.filter(name=name)
