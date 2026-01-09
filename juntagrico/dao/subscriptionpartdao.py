from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.entity.subs import SubscriptionPart
from juntagrico.util.models import q_activated, q_canceled, q_deactivated


class SubscriptionPartDao:
    @staticmethod
    def waiting_extra_subs():
        return SubscriptionPart.objects.filter(type__is_extra=True).filter(~q_activated())

    @staticmethod
    def canceled_extra_subs():
        return SubscriptionPart.objects.filter(type__is_extra=True).filter(q_canceled() & ~q_deactivated())

    @staticmethod
    def waiting_parts_for_active_subscriptions():
        return SubscriptionPart.objects.filter(type__is_extra=False).filter(~q_activated())

    @staticmethod
    def canceled_parts_for_active_subscriptions():
        return SubscriptionPart.objects.filter(type__is_extra=False).filter(q_canceled() & ~q_deactivated()).filter(
            subscription__in=SubscriptionDao.all_active_subscritions().filter(~q_canceled())
        )
