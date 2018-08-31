# -*- coding: utf-8 -*-
from juntagrico.models import Delivery
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao
from juntagrico.entity.subs import Subscription


class DeliveryDao:

    @staticmethod
    def all_deliveries():
        return Delivery.objects.all()

    @staticmethod
    def all_deliveries_order_by_delivery_date_desc():
        return Delivery.objects.all().order_by("-delivery_date")

    @staticmethod
    def deliveries_by_subscription(subscription):
        if subscription is not None:
            member_subscription_size_ids = []
            for subscription_type in subscription.types.all():
                member_subscription_size_ids.append(subscription_type.size)
            member_subscription_weekday = (subscription.depot.weekday % 7) + 1
            return DeliveryDao.all_deliveries_order_by_delivery_date_desc().filter(delivery_date__week_day=member_subscription_weekday).filter(subscription_size__in=member_subscription_size_ids)

        return []
