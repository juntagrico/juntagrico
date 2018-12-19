# -*- coding: utf-8 -*-
import juntagrico


class SubscriptionSizeDao:

    @staticmethod
    def sizes_for_depot_list():
        return juntagrico.models.SubscriptionSize.objects.filter(depot_list=True).order_by('units')

    @staticmethod
    def all_sizes_ordered():
        return juntagrico.models.SubscriptionSize.objects.order_by('units')

    @staticmethod
    def all_visible_sizes_ordered():
        return juntagrico.models.SubscriptionSize.objects.filter(visible=True).order_by('units')

    @staticmethod
    def sizes_by_size(units):
        return juntagrico.models.SubscriptionSize.objects.filter(units=units)

    @staticmethod
    def sizes_by_name(name):
        return juntagrico.models.SubscriptionSize.objects.filter(name=name)
