# -*- coding: utf-8 -*-
import juntagrico


class ExtraSubscriptionDao:

    @staticmethod
    def all_extra_subs():
        return juntagrico.models.ExtraSubscription.objects.all()

    @staticmethod
    def canceled_extra_subs():
        return juntagrico.models.ExtraSubscription.objects.filter(active=True, canceled=True)
        
    @staticmethod
    def waiting_extra_subs():
        return juntagrico.models.ExtraSubscription.objects.filter(active=False, deactivation_date=None)

