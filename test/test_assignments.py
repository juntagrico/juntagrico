from datetime import date

from django.utils import timezone

from juntagrico.entity.subs import SubscriptionPart, Subscription
from juntagrico.entity.subtypes import SubscriptionType
from test.util.test import JuntagricoTestCase


class AssignmentTests(JuntagricoTestCase):

    def setUp(self):
        super().setUp()
        sub_type_data = {
            'name': 'sub_trial_type',
            'long_name': 'sub_type_long_name',
            'size': self.sub_size,
            'shares': 2,
            'visible': True,
            'required_assignments': 10,
            'required_core_assignments': 3,
            'price': 1000,
            'description': 'sub_type_desc'}
        self.sub_trial_type = SubscriptionType.objects.create(trial_days=30, **sub_type_data)

        year = timezone.now().year
        activation_date = date(day=1, month=7, year=year)
        self.sub2.activation_date = activation_date
        SubscriptionPart.objects.create(subscription=self.sub2, type=self.sub_type, activation_date=activation_date)
        activation_date = date(day=1, month=1, year=year)
        deactivation_date = date(day=30, month=6, year=year)
        sub_data = {
            'depot': self.depot,
            'future_depot': None,
            'creation_date': '2017-03-27',
            'start_date': '2018-01-01'
        }
        dates = {
            'activation_date': activation_date,
            'cancellation_date': activation_date,
            'deactivation_date': deactivation_date,
        }
        sub_data3 = {**sub_data, **dates}
        # sub in first half of the year
        self.sub3 = Subscription.objects.create(**sub_data3)
        SubscriptionPart.objects.create(subscription=self.sub3, type=self.sub_type, **dates)
        # trial sub
        self.sub4 = Subscription.objects.create(**sub_data3)
        SubscriptionPart.objects.create(subscription=self.sub4, type=self.sub_trial_type, **dates)
        # ordered, not activated sub
        self.sub5 = Subscription.objects.create(**sub_data)
        SubscriptionPart.objects.create(subscription=self.sub5, type=self.sub_type)

    def testRequiredAssignments(self):
        self.assertEqual(self.sub2.required_assignments, 5)
        self.assertEqual(self.sub2.required_core_assignments, 2)
        self.assertEqual(self.sub3.required_assignments, 5)
        self.assertEqual(self.sub3.required_core_assignments, 1)  # first 6 months or the year are a bit shorter
        self.assertEqual(self.sub4.required_assignments, 10)
        self.assertEqual(self.sub4.required_core_assignments, 3)
        self.assertEqual(self.sub5.required_assignments, 0)
        self.assertEqual(self.sub5.required_core_assignments, 0)
