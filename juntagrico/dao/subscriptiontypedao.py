# -*- coding: utf-8 -*-
import juntagrico


class SubscriptionTypeDao:

    @staticmethod
    def get_all():
        return juntagrico.models.SubscriptionType.objects.all()

    @staticmethod
    def get_by_id(identifier):
        return juntagrico.models.SubscriptionType.objects.filter(id=identifier)

    @staticmethod
    def get_trial():
        return juntagrico.models.SubscriptionType.objects.filter(trial=True)
