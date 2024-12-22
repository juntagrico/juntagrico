from juntagrico.entity.subtypes import SubscriptionProduct


class SubscriptionProductDao:

    @staticmethod
    def get_all_for_depot_list():
        return SubscriptionProduct.objects.filter(sizes__depot_list=True).distinct()
