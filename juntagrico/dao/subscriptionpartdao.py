from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.entity.subs import SubscriptionPart
from juntagrico.util.models import q_activated, q_cancelled, q_isactive, q_deactivated


class SubscriptionPartDao:
    @staticmethod
    def waiting():
        return SubscriptionPart.objects.filter(type__size__product__is_extra=False).filter(~q_activated())

    @staticmethod
    def canceled():
        return SubscriptionPart.objects.filter(type__size__product__is_extra=False).filter(q_cancelled() & ~q_deactivated())

    @staticmethod
    def waiting_extra_subs():
        return SubscriptionPart.objects.filter(type__size__product__is_extra=True).filter(~q_activated())

    @staticmethod
    def canceled_extra_subs():
        return SubscriptionPart.objects.filter(type__size__product__is_extra=True).filter(q_cancelled() & ~q_deactivated())
