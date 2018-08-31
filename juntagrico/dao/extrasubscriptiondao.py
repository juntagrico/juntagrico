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

    @staticmethod
    def extrasubscriptions_by_date(fromdate, tilldate):
        """
        subscriptions that are active in a certain period.
        all subscriptions except those that ended before or
        started after the date range.
        """
        return juntagrico.models.ExtraSubscription.objects.\
            exclude(deactivation_date__lt=fromdate).\
            exclude(activation_date__gt=tilldate)
