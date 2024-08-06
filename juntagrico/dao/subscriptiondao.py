from juntagrico.entity.subs import Subscription
from juntagrico.util.models import q_deactivated, q_activated, q_canceled, q_isactive


class SubscriptionDao:

    @staticmethod
    def all_subscritions():
        return Subscription.objects.all()

    @staticmethod
    def active_subscritions_by_depot(depot):
        return Subscription.objects.filter(depot=depot).filter(q_isactive())

    @staticmethod
    def all_active_subscritions():
        return Subscription.objects.filter(q_isactive())

    @staticmethod
    def not_started_subscriptions():
        return Subscription.objects.filter(~q_activated()).order_by('start_date')

    @staticmethod
    def future_subscriptions():
        return Subscription.objects.filter(~q_canceled() & ~q_deactivated()).filter(deactivation_date=None)

    @staticmethod
    def canceled_subscriptions():
        return Subscription.objects.filter(q_canceled() & ~q_deactivated()).order_by('end_date')
