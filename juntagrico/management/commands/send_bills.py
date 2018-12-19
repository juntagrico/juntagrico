from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils import bills

from juntagrico.config import Config

from juntagrico.models import *
from juntagrico.dao.extrasubbillingperioddao import ExtraSubBillingPeriodDao
from juntagrico.dao.subscriptiondao import SubscriptionDao


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):
        now = timezone.now()
        periods = ExtraSubBillingPeriodDao.get_starting_for_date(now)
        for period in periods:
            for extra in period.type.extra_subscriptions.filter(active=True):
                bill_extra_subscription(extra, period)
        bs = Config.business_year_start()
        if now.day == bs['day'] and now.month == bs['month']:
            for subscription in SubscriptionDao.all_active_subscritions():
                bill_subscription(subscrtption)
