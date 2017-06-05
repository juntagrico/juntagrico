# -*- coding: utf-8 -*-
from django.utils import timezone
from django.db.models import Q

import juntagrico


class ExtraSubBillingPeriodDao:
    def __init__(self):
        pass

    @staticmethod
    def get_current_period_per_type(type):        
        now = timezone.now()
        month = now.month
        for period in juntagrico.entity.billing.ExtraSubBillingPeriod.objects.filter(type__id=type.id).filter(
            start_month__gte=month).filter(end_month__lte=month):
            start = period.get_actual_start()
            end = period.get_actual_end()
            if start <= now <= end:
                return period
    
    def get_starting_for_date(date):
        day = date.day
        month = date.month
        return juntagrico.entity.billing.ExtraSubBillingPeriod.objects.filter(start_month=month).filter(start_day=day)