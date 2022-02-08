from django.utils import timezone

import juntagrico


class BillingPeriodDao:

    @staticmethod
    def get_current_period_per_type(type):
        now = timezone.now()
        month = now.month
        for period in juntagrico.entity.billing.BillingPeriod.objects.filter(type__id=type.id).filter(
                start_month__lte=month).filter(end_month__gte=month):
            start = period.get_actual_start()
            end = period.get_actual_end()
            if start <= now.date() <= end:
                return period
        return None

    def get_starting_for_date(date):
        day = date.day
        month = date.month
        return juntagrico.entity.billing.BillingPeriod.objects.filter(start_month=month).filter(start_day=day)
