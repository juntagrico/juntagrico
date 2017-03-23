# -*- coding: utf-8 -*-

from juntagrico.models import *


class ShareDao:
    def __init__(self):
        pass

    @staticmethod
    def paid_shares(subscription):
        return Share.objects.filter(member__in=subscription.members.all()).filter(paid_date__isnull=False).filter(
            cancelled_date__isnull=True)
