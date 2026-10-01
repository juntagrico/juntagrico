from datetime import date, timedelta

from juntagrico.entity.subs import Subscription, SubscriptionSurcharge
from . import JuntagricoTestCase


class AssignmentTests(JuntagricoTestCase):
    year = 2022
    activation_date = date(day=1, month=1, year=year)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.sub_trial_type = cls.create_sub_type(cls.bundle, trial_days=30)
        cls.subs = [
            # sub in second half of the year
            cls.create_sub(cls.depot, cls.sub_type, date(day=1, month=7, year=cls.year)),
            # sub in first half of the year
            cls.create_sub(cls.depot, cls.sub_type, cls.activation_date, deactivation_date=date(day=30, month=6, year=cls.year)),
            # trial sub ongoing
            cls.create_sub(cls.depot, cls.sub_trial_type, cls.activation_date, ),
            # trial sub shorter than planned
            cls.create_sub(cls.depot, cls.sub_trial_type, cls.activation_date, deactivation_date=date(day=15, month=1, year=cls.year)),
            # trial sub longer than planned
            cls.create_sub(cls.depot, cls.sub_trial_type, cls.activation_date, deactivation_date=date(day=1, month=3, year=cls.year)),
            # trial sub at the end of the year
            cls.create_sub(cls.depot, cls.sub_trial_type, date(day=15, month=12, year=cls.year)),
            # trial sub starting last year
            cls.create_sub(cls.depot, cls.sub_trial_type, date(day=15, month=12, year=cls.year - 1)),
            # ordered, not activated sub
            cls.create_sub(cls.depot, cls.sub_type),
            # multiple parts
            cls.create_sub(cls.depot, [cls.sub_type, cls.sub_type], cls.activation_date),
            # with surcharges
            cls.create_sub(cls.depot, cls.sub_type, cls.activation_date),
        ]
        SubscriptionSurcharge.objects.create(
            subscription=cls.subs[9],
            amount=0,
            required_assignments=2,
            required_core_assignments=2,
            description='surcharge',
            date=cls.activation_date,
        )
        # out of date range surcharge should have no impact 
        SubscriptionSurcharge.objects.create(
            subscription=cls.subs[9],
            amount=0,
            required_assignments=100,
            required_core_assignments=100,
            description='surcharge',
            date=cls.activation_date - timedelta(days=1),
        )

    def testRequiredAssignments(self):
        # get assignments for entire year.
        subs = Subscription.objects.annotate_required_assignments(self.activation_date, date(self.year, 12, 31)).filter(pk__in=self.subs).distinct()
        subs = {sub.id: sub for sub in subs}
        # sub in second half of the year
        self.assertEqual(subs[self.subs[0].id].required_assignments, 5)
        self.assertEqual(subs[self.subs[0].id].required_core_assignments, 2)
        # sub in first half of the year
        self.assertEqual(subs[self.subs[1].id].required_assignments, 5)
        self.assertEqual(subs[self.subs[1].id].required_core_assignments, 1)  # first 6 months or the year are a bit shorter
        # trial sub ongoing
        self.assertEqual(subs[self.subs[2].id].required_assignments, 10)
        self.assertEqual(subs[self.subs[2].id].required_core_assignments, 3)
        # trial sub shorter than normal trial period -> should not impact required assignments
        self.assertEqual(subs[self.subs[3].id].required_assignments, 10)
        self.assertEqual(subs[self.subs[3].id].required_core_assignments, 3)
        # trial sub longer than normal trial period -> should not impact required assignments
        self.assertEqual(subs[self.subs[4].id].required_assignments, 10)
        self.assertEqual(subs[self.subs[4].id].required_core_assignments, 3)
        # trial sub at the end of the year
        self.assertEqual(subs[self.subs[5].id].required_assignments, 6)  # 17/30 rounded
        self.assertEqual(subs[self.subs[5].id].required_core_assignments, 2)
        # trial sub starting last year
        self.assertEqual(subs[self.subs[6].id].required_assignments, 4)  # 13/30 rounded
        self.assertEqual(subs[self.subs[6].id].required_core_assignments, 1)
        # ordered, not activated sub
        self.assertEqual(subs[self.subs[7].id].required_assignments, 0)
        self.assertEqual(subs[self.subs[7].id].required_core_assignments, 0)
        # multiple parts
        self.assertEqual(subs[self.subs[8].id].required_assignments, 20)
        self.assertEqual(subs[self.subs[8].id].required_core_assignments, 6)
        # with surcharge
        self.assertEqual(subs[self.subs[9].id].required_assignments, 12)
        self.assertEqual(subs[self.subs[9].id].required_core_assignments, 5)
