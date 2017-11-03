# -*- coding: utf-8 -*-

import juntagrico


class ShareDao:

    @staticmethod
    def paid_shares(subscription):
        return juntagrico.models.Share.objects.filter(member__in=subscription.members.all()).filter(paid_date__isnull=False).filter(
            cancelled_date__isnull=True)
            
    @staticmethod
    def all_shares_subscription(subscription):
        return juntagrico.models.Share.objects.filter(member__in=subscription.members.all()).filter(
            cancelled_date__isnull=True)
            
    @staticmethod
    def unpaid_shares(member):
        return juntagrico.models.Share.objects.filter(member=member).filter(paid_date__isnull=True)
