# -*- coding: utf-8 -*-

from juntagrico.models import *


class SubscriptionDao:

    @staticmethod
    def all_subscritions():
        return Subscription.objects.all()

    @staticmethod
    def subscritions_by_depot(depot):
        return Subscription.objects.filter(depot=depot)

    @staticmethod
    def subscritions_with_future_depots():
        return Subscription.objects.exclude(future_depot__isnull=True)

    @staticmethod
    def all_active_subscritions():
        return Subscription.objects.filter(active=True)

    @staticmethod
    def not_started_subscriptions():
        return Subscription.objects.filter(active=False).filter(deactivation_date=None).order_by('start_date')

    @staticmethod
    def future_subscriptions():
        return Subscription.objects.filter(canceled=False).filter(deactivation_date=None)

    @staticmethod
    def canceled_subscriptions():
        return Subscription.objects.filter(active=True).filter(canceled=True).order_by('end_date')

    @staticmethod
    def subscriptions_by_date(fromdate, tilldate):
        """
        subscriptions that are active in a certain period
        all subscriptions except those that ended before or
        started after our date range.
        """
        return Subscription.objects.\
            exclude(deactivation_date__lt=fromdate).exclude(
                activation_date__gt=tilldate)
