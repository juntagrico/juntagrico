import django.test
from datetime import date
from django.conf import settings

from test.subscription_test_base import SubscriptionTestBase
from juntagrico.models import Subscription, Depot, Member, SubscriptionSize
from juntagrico.models import SubscriptionType, TSST
from juntagrico.util.bills import scale_subscription_price


class ScaleSuscriptionPriceTest(SubscriptionTestBase):

    def test_price_by_date_fullyear(self):
        start_date = date(2018, 1, 1)
        end_date = date(2018, 12, 31)
        price_fullyear = scale_subscription_price(self.subscription,
                                                    start_date, end_date)
        self.assertEqual(1200.0, price_fullyear, "full year")

    def test_price_by_date_shifted_business_year(self):
        settings.BUSINESS_YEAR_START = {'day': 1, 'month': 7}
        try:
            start_date = date(2018, 7, 1)
            end_date = date(2019, 6, 30)
            price_fullyear = scale_subscription_price(self.subscription,
                                                        start_date, end_date)
            self.assertEqual(1200.0, price_fullyear, "full year")
        finally:
            del settings.BUSINESS_YEAR_START

    def test_price_by_date_quarter(self):
        start_date = date(2018, 4, 1)
        end_date = date(2018, 6, 30)
        price_quarter = scale_subscription_price(self.subscription,
                                                    start_date, end_date)
        price_quarter_expected = 1200.0 * (30 + 31 + 30) / 365
        self.assertEqual(price_quarter_expected, price_quarter,
                            "second quarter")

    def test_price_by_date_partial_subscription(self):
        self.subscription.activation_date = date(2018, 7, 1)
        self.subscription.deactivation_date = date(2018, 9, 30)
        start_date = date(2018, 1, 1)
        end_date = date(2018, 12, 31)
        price = scale_subscription_price(self.subscription,
                                        start_date, end_date)
        price_expected = 1200.0 * (31 + 31 + 30) / 365
        self.assertEqual(price_expected, price,
                            "quarter subscription over a year")
