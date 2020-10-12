from juntagrico.entity.subtypes import SubscriptionProduct


class SubscriptionProductDao:

    @staticmethod
    def get_all():
        return SubscriptionProduct.objects.all()

    @staticmethod
    def get_all_visible():
        return SubscriptionProduct.objects.filter(sizes__visible=True).distinct()

    @staticmethod
    def get_all_for_depot_list():
        return SubscriptionProduct.objects.filter(sizes__depot_list=True).distinct()
