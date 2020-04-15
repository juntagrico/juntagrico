from juntagrico.entity.subs import SubscriptionPart


class SubscriptionPartDao:

    @staticmethod
    def get_canceled_for_subscription(subscription):
        return SubscriptionPart.objects.filter(subscription=subscription, cancellation_date__isnull=False)

    @staticmethod
    def get_waiting_for_subscription(subscription):
        return SubscriptionPart.objects.filter(subscription=subscription, activation_date__isnull=False)
