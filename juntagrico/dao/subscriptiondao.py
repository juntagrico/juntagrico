from juntagrico.entity.subs import Subscription
from juntagrico.util.models import q_deactivated, q_activated, q_cancelled, q_isactive


class SubscriptionDao:

    @staticmethod
    def all_subscritions():
        return Subscription.objects.all()

    @staticmethod
    def active_subscritions_by_depot(depot):
        return SubscriptionDao.all_active_subscritions().filter(depot=depot)

    @staticmethod
    def subscritions_with_future_depots():
        return Subscription.objects.exclude(future_depot__isnull=True)

    @staticmethod
    def all_active_subscritions():
        return Subscription.objects.active_on()
