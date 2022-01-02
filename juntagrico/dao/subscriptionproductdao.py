from juntagrico.entity.subtypes import SubscriptionProduct


class SubscriptionProductDao:

    @staticmethod
    def get_all():
        return SubscriptionProduct.objects.all()

    @staticmethod
    def get_all_visible():
        return SubscriptionProduct.objects.filter(sizes__visible=True).distinct()

    @staticmethod
    def get_normal_products():
        return SubscriptionProduct.objects.filter(is_extra=False)

    @staticmethod
    def get_visible_normal_products():
        return SubscriptionProduct.objects.filter(sizes__visible=True, is_extra=False).distinct()

    @staticmethod
    def all_extra_products():
        return SubscriptionProduct.objects.filter(is_extra=True)

    @staticmethod
    def all_visible_extra_products():
        return SubscriptionProduct.objects.filter(sizes__visible=True, is_extra=True).distinct()

    @staticmethod
    def get_all_for_depot_list():
        return SubscriptionProduct.objects.filter(sizes__depot_list=True).distinct()
