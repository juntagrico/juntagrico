# -*- coding: utf-8 -*-
import juntagrico


class SubscriptionProductDao:

    @staticmethod
    def get_all():
        return juntagrico.models.SubscriptionProduct.objects.all()
