from juntagrico.entity.subtypes import SubscriptionProduct


class SubscriptionProductDao:

    @staticmethod
    def get_all():
        return SubscriptionProduct.objects.all()
