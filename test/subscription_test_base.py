import django.test
from datetime import date
from juntagrico.models import *


class SubscriptionTestBase(django.test.TestCase):
    """
    base class for subscription tests.
    defines setUp method that creates test data.
    """
    def setUp(self):
        member = Member.objects.create(
            first_name="Michael",
            last_name="Test",
            email="test@test.ch",
            addr_street="Musterstrasse",
            addr_zipcode="8000",
            addr_location="Zürich",
            phone="01234567"
            )

        subs_size = SubscriptionSize.objects.create(
            name="Normal",
            long_name="Normale Grösse",
            units=1
            )

        subs_type = SubscriptionType.objects.create(
            name="Normal",
            size=subs_size,
            shares=1,
            required_assignments=5,
            price=1200,
            )

        depot = Depot.objects.create(
            code="Depot 1",
            name="Das erste Depot",
            contact=member,
            weekday=5,
            )

        self.subscription = Subscription.objects.create(
            depot=depot,
            primary_member=member,
            active=True,
            activation_date=date(2018, 1, 1)
            )
        TSST.objects.create(
            subscription=self.subscription,
            type=subs_type
            )
