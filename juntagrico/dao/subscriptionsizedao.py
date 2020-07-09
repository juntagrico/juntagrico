from juntagrico.entity.subtypes import SubscriptionSize


class SubscriptionSizeDao:

    @staticmethod
    def sizes_for_depot_list():
        return SubscriptionSize.objects.filter(depot_list=True).order_by('units')

    @staticmethod
    def all_sizes_ordered():
        return SubscriptionSize.objects.order_by('product', 'units')

    @staticmethod
    def all_visible_sizes_ordered():
        return SubscriptionSize.objects.filter(visible=True).order_by('units')

    @staticmethod
    def sizes_by_size(units):
        return SubscriptionSize.objects.filter(units=units)

    @staticmethod
    def sizes_by_name(name):
        return SubscriptionSize.objects.filter(name=name)
