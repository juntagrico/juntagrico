from juntagrico.entity.subs import SubscriptionPart
from juntagrico.util.models import q_activated, q_cancelled


class SubscriptionPartDao:

    @staticmethod
    def get_canceled_for_subscription(subscription):
        return SubscriptionPart.objects.filter(subscription=subscription).filter(q_cancelled())

    @staticmethod
    def get_waiting_for_subscription(subscription):
        return SubscriptionPart.objects.filter(subscription=subscription).filter(~q_activated())
