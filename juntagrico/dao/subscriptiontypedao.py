from juntagrico.entity.subtypes import SubscriptionType


class SubscriptionTypeDao:

    @staticmethod
    def get_all():
        return SubscriptionType.objects.all()

    @staticmethod
    def get_by_id(identifier):
        return SubscriptionType.objects.filter(id=identifier)
