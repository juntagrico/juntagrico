import datetime

from django.core import mail
from django.urls import reverse

from juntagrico.entity.subs import SubscriptionPart
from juntagrico.tests import JuntagricoTestCaseWithShares


class TrialSubscriptionTestCase(JuntagricoTestCaseWithShares):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.trial_sub_type = cls.create_sub_type(cls.sub_size, trial_days=30)
        cls.trial_member1 = cls.create_member('trial1@example.com')
        cls.trial_sub1 = cls.create_sub(cls.depot, cls.trial_sub_type)
        cls.trial_member1.join_subscription(cls.trial_sub1, True)
        cls.trial_part1 = cls.trial_sub1.parts.first()
        cls.default_member = cls.trial_member1


class TrialSubscriptionTests(TrialSubscriptionTestCase):
    def testCancelTrial(self):
        self.assertGet(reverse('part-cancel', args=[self.trial_part1.id]), 302)
        self.trial_part1.refresh_from_db()
        self.assertTrue(self.trial_part1.canceled)

    def testContinueTrial(self):
        mail.outbox.clear()
        self.trial_sub1.activate()
        self.assertGet(reverse('part-continue', args=[self.trial_part1.id]))
        post_data = {'part_type': self.sub_type3.id}
        self.assertPost(reverse('part-continue', args=[self.trial_part1.pk]), post_data, code=302)
        self.trial_sub1.refresh_from_db()
        # check: has 2 parts now.
        self.assertEqual(self.trial_sub1.parts.count(), 2)
        # check: has only one uncanceled part with new type
        self.assertEqual(self.trial_sub1.future_parts.count(), 1)
        self.assertEqual(self.trial_sub1.future_parts.first().type, self.sub_type3)
        # check: previous part is still there
        self.trial_part1.refresh_from_db()
        self.assertEqual(self.trial_part1.type, self.trial_sub_type)
        self.assertTrue(self.trial_part1.canceled)
        # check notification was sent to admins
        self.assertEqual(len(mail.outbox), 2)

    def testContinueTrialBeforeActivation(self):
        mail.outbox.clear()
        # part type should just change.
        post_data = {'part_type': self.sub_type3.id}
        self.assertPost(reverse('part-continue', args=[self.trial_part1.pk]), post_data, code=302)
        self.trial_sub1.refresh_from_db()
        # check: has only one part with new type
        self.assertEqual(self.trial_sub1.parts.count(), 1)
        self.assertEqual(self.trial_sub1.parts.first().type, self.sub_type3)
        # no notifications in that case
        self.assertEqual(len(mail.outbox), 0)


class WaitingTrialSubscriptionAdminTests(TrialSubscriptionTestCase):
    def testManagementList(self):
        self.assertGet(reverse('manage-sub-trial'), member=self.admin)

    def testActivateTrial(self):
        self.assertGet(reverse('manage-trial-activate', args=[self.trial_part1.pk]), 302, member=self.admin)
        self.trial_part1.refresh_from_db()
        self.assertTrue(self.trial_part1.active)

    def testCancelTrialByAdmin(self):
        mail.outbox.clear()
        self.assertGet(reverse('manage-part-cancel', args=[self.trial_part1.id]), 302, member=self.admin)
        self.trial_part1.refresh_from_db()
        self.assertTrue(self.trial_part1.canceled)
        self.assertEqual(len(mail.outbox), 1)  # notification to member


class ActiveTrialSubscriptionAdminTests(TrialSubscriptionTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.trial_sub1.activate()
        cls.trial_part1.refresh_from_db()

    def testManagementList(self):
        self.assertGet(reverse('manage-sub-trial'), member=self.admin)

    def testContinueTrialByAdmin(self):
        mail.outbox.clear()
        self.assertGet(reverse('manage-trial-continue', args=[self.trial_part1.pk]), member=self.admin)
        post_data = {'part_type': self.sub_type3.id}
        self.assertPost(reverse('manage-trial-continue', args=[self.trial_part1.pk]), post_data, 302, member=self.admin)
        self.trial_sub1.refresh_from_db()
        # check: has 2 parts now.
        self.assertEqual(self.trial_sub1.parts.count(), 2)
        # check: has only one uncanceled part with new type
        self.assertEqual(self.trial_sub1.future_parts.count(), 1)
        self.assertEqual(self.trial_sub1.future_parts.first().type, self.sub_type3)
        # check: previous part is still there
        self.trial_part1.refresh_from_db()
        self.assertEqual(self.trial_part1.type, self.trial_sub_type)
        self.assertTrue(self.trial_part1.canceled)
        self.assertEqual(len(mail.outbox), 1)  # notification to member

    def testDeactivateTrial(self):
        self.assertGet(reverse('manage-trial-deactivate', args=[self.trial_part1.pk]), 302, member=self.admin)
        self.trial_part1.refresh_from_db()
        self.assertEqual(self.trial_part1.deactivation_date, self.trial_part1.activation_date + datetime.timedelta(30))

    def testDeactivateTrialOnDate(self):
        data = {'end_date': self.trial_sub1.activation_date}
        self.assertPost(reverse('manage-trial-deactivate', args=[self.trial_part1.pk]), data, 302, member=self.admin)
        self.trial_part1.refresh_from_db()
        self.assertTrue(self.trial_part1.inactive)


class ContinueTrialSubscriptionAdminTests(TrialSubscriptionTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.activation_date = datetime.date(2025, 4, 24)
        cls.trial_sub1.activate(cls.activation_date)
        cls.trial_part1.refresh_from_db()
        cls.follow_up_part = SubscriptionPart.objects.create(subscription=cls.trial_sub1, type=cls.sub_type)
        cls.trial_part1.cancel()

    def testManagementList(self):
        self.assertGet(reverse('manage-sub-trial'), member=self.admin)

    def testCloseoutReplaceTrial(self):
        self.assertGet(reverse('manage-trial-closeout', args=[self.trial_part1.pk]), member=self.admin)
        data = {'mode': 'replace'}
        self.assertPost(reverse('manage-trial-closeout', args=[self.trial_part1.pk]), data, 302, member=self.admin)
        self.trial_sub1.refresh_from_db()
        self.assertEqual(self.trial_sub1.parts.count(), 1)
        self.assertEqual(self.trial_sub1.parts.first().type, self.follow_up_part.type)

    def testCloseoutAppendTrial(self):
        self.assertGet(reverse('manage-trial-closeout', args=[self.trial_part1.pk]), member=self.admin)
        data = {
            'mode': 'append',
            'deactivation_mode': 'by_end',
            'activation_mode': 'next_day',
        }
        self.assertPost(reverse('manage-trial-closeout', args=[self.trial_part1.pk]), data, 302, member=self.admin)
        self.trial_sub1.refresh_from_db()
        self.assertEqual(self.trial_sub1.parts.count(), 2)
        self.follow_up_part.refresh_from_db()
        self.assertEqual(self.follow_up_part.activation_date, self.activation_date + datetime.timedelta(days=31))
        self.trial_part1.refresh_from_db()
        self.assertEqual(self.trial_part1.deactivation_date, self.activation_date + datetime.timedelta(days=30))

    def testCloseoutAppendByDatesTrial(self):
        data = {
            'mode': 'append',
            'deactivation_mode': 'by_date',
            'deactivation_date': '1.5.2025',
            'activation_mode': 'by_date',
            'activation_date': '2.5.2025',
        }
        self.assertPost(reverse('manage-trial-closeout', args=[self.trial_part1.pk]), data, 302, member=self.admin)
        self.trial_sub1.refresh_from_db()
        self.assertEqual(self.trial_sub1.parts.count(), 2)
        self.trial_part1.refresh_from_db()
        self.assertEqual(self.trial_part1.deactivation_date, datetime.date(2025, 5, 1))
        self.follow_up_part.refresh_from_db()
        self.assertEqual(self.follow_up_part.activation_date, datetime.date(2025, 5, 2))

    def testCloseoutTrialWithOtherParts(self):
        other_sub_size = self.create_sub_size('other size', self.sub_product, units=2)
        other_sub_size_type = self.create_sub_type(other_sub_size)
        other_part = SubscriptionPart.objects.create(subscription=self.trial_sub1, type=other_sub_size_type)
        data = {
            'mode': 'replace',
            f'activate{other_part.id}': 'by_date',
            f'activation_date{other_part.id}': '3.5.2025',
        }
        self.assertPost(reverse('manage-trial-closeout', args=[self.trial_part1.pk]), data, 302, member=self.admin)
        self.trial_sub1.refresh_from_db()
        self.assertEqual(self.trial_sub1.parts.count(), 2)
        self.follow_up_part.refresh_from_db()
        self.assertEqual(self.follow_up_part.activation_date, self.activation_date)
        other_part.refresh_from_db()
        self.assertEqual(other_part.activation_date, datetime.date(2025, 5, 3))


class ContinueTrialWithOtherSubscriptionAdminTests(TrialSubscriptionTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.activation_date = datetime.date(2025, 4, 24)
        cls.trial_sub1.activate(cls.activation_date)
        cls.trial_part1.refresh_from_db()
        other_sub_size = cls.create_sub_size('other size', cls.sub_product, units=2)
        other_sub_size_type = cls.create_sub_type(other_sub_size)
        cls.other_part = SubscriptionPart.objects.create(subscription=cls.trial_sub1, type=other_sub_size_type)
        cls.trial_part1.cancel()

    def testManagementList(self):
        self.assertGet(reverse('manage-sub-trial'), member=self.admin)

    def testCloseoutTrialWithOnlyOtherSize(self):
        data = {
            'deactivation_mode': 'by_end',
            f'activate{self.other_part.id}': 'by_date',
            f'activation_date{self.other_part.id}': '5.5.2025',
        }
        self.assertPost(reverse('manage-trial-closeout', args=[self.trial_part1.pk]), data, 302, member=self.admin)
        self.trial_sub1.refresh_from_db()
        self.assertEqual(self.trial_sub1.parts.count(), 2)
        self.trial_part1.refresh_from_db()
        self.assertEqual(self.trial_part1.deactivation_date, self.activation_date + datetime.timedelta(days=30))
        self.other_part.refresh_from_db()
        self.assertEqual(self.other_part.activation_date, datetime.date(2025, 5, 5))
