from datetime import date

from django.utils import timezone

from test.util.test import JuntagricoTestCase


class AssignmentTests(JuntagricoTestCase):

    def setUp(self):
        super().setUp()
        self.sub_trial_type = self.create_sub_type(self.sub_size, trial_days=30)

        # sub in second half of the year
        year = timezone.now().year
        self.sub2 = self.create_sub(self.depot, date(day=1, month=7, year=year), parts=[self.sub_type])
        # sub in first half of the year
        activation_date = date(day=1, month=1, year=year)
        self.sub3 = self.create_sub(self.depot, activation_date, deactivation_date=date(day=30, month=6, year=year), parts=[self.sub_type])
        # trial sub ongoing
        self.sub41 = self.create_sub(self.depot, activation_date, [self.sub_trial_type])
        # trial sub shorter than planned
        self.sub42 = self.create_sub(self.depot, activation_date, deactivation_date=date(day=15, month=1, year=year), parts=[self.sub_trial_type])
        # trial sub at the end of the year
        self.sub43 = self.create_sub(self.depot, date(day=15, month=12, year=year), [self.sub_trial_type])
        # trial sub starting last year
        self.sub44 = self.create_sub(self.depot, date(day=15, month=12, year=year - 1), [self.sub_trial_type])
        # ordered, not activated sub
        self.sub5 = self.create_sub(self.depot, parts=[self.sub_type])

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
