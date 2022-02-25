from django.db.models import QuerySet, Manager

from juntagrico.util.models import q_activated, q_cancelled, q_deactivated


class SubscriptionPartQuerySet(QuerySet):
    def waiting(self):
        return self.filter(~q_activated())

    def cancelled(self):
        return self.filter(q_cancelled() & ~q_deactivated())

    def in_active_subscription(self):
        from juntagrico.entity.subs import Subscription
        return self.filter(subscription__in=Subscription.objects.active().filter(~q_cancelled()))

    def for_depot_list(self):
        return self.filter(sizes__depot_list=True).distinct()


class NormalSubscriptionPartManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type__size__product__is_extra=False)


class ExtraSubscriptionPartManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type__size__product__is_extra=True)
