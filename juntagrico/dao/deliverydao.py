# -*- coding: utf-8 -*-
from juntagrico.models import Delivery


class DeliveryDao:

    @staticmethod
    def all_deliveries():
        return Delivery.objects.all()
    
    @staticmethod
    def all_deliveries_order_by_delivery_date_desc():
        return Delivery.objects.all().order_by("-delivery_date")
    
    @staticmethod
    def deliveries_by_weekday_and_subscription_size(weekday, subscription_size):
        return Delivery.objects.all().filter(weekday=weekday).filter(subscription_size=subscription_size)