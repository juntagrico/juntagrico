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

        # sub in second half of the year
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
        # trial sub ongoing
        sub_data4 = {**sub_data, 'activation_date': activation_date}
        self.sub41 = Subscription.objects.create(**sub_data4)
        SubscriptionPart.objects.create(subscription=self.sub41, type=self.sub_trial_type, activation_date=activation_date)
        # trial sub shorter than planned
        self.sub42 = Subscription.objects.create(**sub_data3)
        dates_short = {**dates, 'deactivation_date': date(day=15, month=1, year=year)}
        SubscriptionPart.objects.create(subscription=self.sub42, type=self.sub_trial_type, **dates_short)
        # trial sub at the end of the year
        dates_year_end = {
            'activation_date': date(day=15, month=12, year=year),
            'cancellation_date': date(day=15, month=12, year=year),
        }
        sub_data43 = {**sub_data, **dates_year_end}
        self.sub43 = Subscription.objects.create(**sub_data43)
        SubscriptionPart.objects.create(subscription=self.sub43, type=self.sub_trial_type, **dates_year_end)
        # trial sub starting last year
        dates_year_last = {'activation_date': date(day=15, month=12, year=year - 1)}
        sub_data44 = {**sub_data, **dates_year_last}
        self.sub44 = Subscription.objects.create(**sub_data44)
        SubscriptionPart.objects.create(subscription=self.sub44, type=self.sub_trial_type, **dates_year_last)
        # ordered, not activated sub
        self.sub5 = Subscription.objects.create(**sub_data)
        SubscriptionPart.objects.create(subscription=self.sub5, type=self.sub_type)

    def testRequiredAssignments(self):
        # sub in second half of the year
        self.assertEqual(self.sub2.required_assignments, 5)
        self.assertEqual(self.sub2.required_core_assignments, 2)
        # sub in first half of the year
        self.assertEqual(self.sub3.required_assignments, 5)
        self.assertEqual(self.sub3.required_core_assignments, 1)  # first 6 months or the year are a bit shorter
        # trial sub ongoing
        self.assertEqual(self.sub41.required_assignments, 10)
        self.assertEqual(self.sub41.required_core_assignments, 3)
        # trial sub shorter than normal trial period
        self.assertEqual(self.sub42.required_assignments, 5)
        self.assertEqual(self.sub42.required_core_assignments, 2)
        # trial sub at the end of the year
        self.assertEqual(self.sub43.required_assignments, 6)  # 17/30 rounded
        self.assertEqual(self.sub43.required_core_assignments, 2)
        # trial sub starting last year
        self.assertEqual(self.sub44.required_assignments, 4)  # 13/30 rounded
        self.assertEqual(self.sub44.required_core_assignments, 1)
        # ordered, not activated sub
        self.assertEqual(self.sub5.required_assignments, 0)
        self.assertEqual(self.sub5.required_core_assignments, 0)
