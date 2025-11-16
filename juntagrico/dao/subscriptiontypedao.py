from juntagrico.entity.subtypes import SubscriptionType


class SubscriptionTypeDao:

    @staticmethod
    def get_all():
        return SubscriptionType.objects.all()

    @staticmethod
    def get_normal_visible():
        return SubscriptionType.objects.filter(visible=True, size__visible=True, size__product__is_extra=False)

    @staticmethod
    def get_with_core():
        return SubscriptionType.objects.filter(required_core_assignments__gt=0)

    @staticmethod
    def get_by_id(identifier):
        return SubscriptionType.objects.filter(id=identifier)
