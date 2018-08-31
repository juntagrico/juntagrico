# -*- coding: utf-8 -*-
import juntagrico


class SubscriptionTypeDao:

    @staticmethod
    def get_by_id(identifier):
        return juntagrico.models.SubscriptionType.objects.filter(id=identifier)
