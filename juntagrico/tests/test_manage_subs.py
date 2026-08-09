from django.core import mail
from django.test import override_settings, tag
from django.urls import reverse

from . import JuntagricoTestCase, JuntagricoTestCaseWithShares
from ..entity.share import Share
from ..entity.subs import SubscriptionPart


class ManageSubPendingListTests(JuntagricoTestCase):
    activation_notifications = 1
    deactivation_notifications = 1

    def testSubscriptionPendingList(self):
        response = self.assertGet(reverse('manage-sub-pending'))
        # check that list is correct
        objects = response.context['object_list']
        self.assertEqual(set(objects.order_by('id')), {self.canceled_sub, self.sub2})

    def testSubscriptionActivateNoAccess(self):
        # member2 has no access
        self.assertGet(reverse('manage-sub-pending'), member=self.member2, code=403)
        self.assertPost(reverse('parts-apply'), member=self.member2, code=302)

    def testSubscriptionActivate(self):
        self.assertGet(reverse('parts-apply'), code=302)
        self.assertFalse(self.sub2.parts.first().active)
        # test activation
        self.assertFalse(self.area.members.filter(pk__in=self.sub2.current_members).exists())
        part = self.sub2.parts.first()
        self.assertPost(reverse('parts-apply'), {'parts[]': [part.id]}, code=302)
        # check that part is active
        part.refresh_from_db()
        self.assertTrue(part.active)
        # check that members of sub2 where added to area
        self.assertQuerySetEqual(self.area.members.filter(pk__in=self.sub2.current_members), self.sub2.current_members)
        self.assertEqual(len(mail.outbox), self.activation_notifications)

    def testSubscriptionDeactivate(self):
        self.assertGet(reverse('parts-apply'), code=302)
        self.assertTrue(self.canceled_sub.parts.first().active)
        # test deactivate
        part = self.canceled_sub.parts.first()
        self.assertPost(reverse('parts-apply'), {'parts[]': [part.id]}, code=302)
        # check that part is deactivated
        part.refresh_from_db()
        self.assertFalse(part.active)
        self.assertEqual(len(mail.outbox), self.deactivation_notifications)

    def testSubscriptionChange(self):
        self.assertGet(reverse('parts-apply'), code=302)
        deactivate_part = self.canceled_sub.parts.first()
        activate_part = SubscriptionPart.objects.create(subscription=self.canceled_sub, type=self.sub_type)
        self.assertTrue(deactivate_part.active)
        self.assertFalse(activate_part.active)
        # test change
        self.assertPost(reverse('parts-apply'), {'parts[]': [deactivate_part.id, activate_part.id]}, code=302)
        # check that part is deactivated
        deactivate_part.refresh_from_db()
        activate_part.refresh_from_db()
        self.assertFalse(deactivate_part.active)
        self.assertTrue(activate_part.active)
        self.assertEqual(len(mail.outbox), 1)  # 1 combined notification email


class ManageSubPendingListChangeDateTests(ManageSubPendingListTests):
    def setUp(self):
        super().setUp()
        session = self.client.session
        session['changedate'] = '2026-06-21'
        session.save()


@override_settings(DISABLE_NOTIFICATIONS=['subscription_activated'])
class ManageSubPendingListNoActivationNotificationTests(ManageSubPendingListTests):
    activation_notifications = 0


@override_settings(DISABLE_NOTIFICATIONS=['subscription_deactivated'])
class ManageSubPendingListNoDeactivationNotificationTests(ManageSubPendingListTests):
    deactivation_notifications = 0


class ManageSubRecentListTests(JuntagricoTestCase):
    def testSubscriptionRecentList(self):
        response = self.assertGet(reverse('manage-sub-recent'))
        # check that list is correct
        self.assertEqual(set(response.context['ordered_parts']), {
            *self.sub3.parts.all(), *self.sub.parts.all(), *self.sub2.parts.all(), *self.canceled_sub.parts.all(),
            *self.deactivated_sub.parts.all()
        })
        self.assertEqual(set(response.context['activated_parts']), {
            *self.sub3.parts.all(), *self.sub.parts.all(), *self.canceled_sub.parts.all(),
            *self.deactivated_sub.parts.all()
        })
        self.assertEqual(set(response.context['canceled_parts']), {
            *self.sub3.parts.all(), *self.canceled_sub.parts.all(), *self.deactivated_sub.parts.all()
        })
        self.assertEqual(set(response.context['deactivated_parts']), {
            *self.sub3.parts.all()
        })
        self.assertEqual(set(response.context['joined_memberships']), {
            *self.sub3.subscriptionmembership_set.all(), *self.sub.subscriptionmembership_set.all(),
            *self.canceled_sub.subscriptionmembership_set.all(), *self.deactivated_sub.subscriptionmembership_set.all()
        })
        self.assertEqual(set(response.context['left_memberships']), {
            *self.sub3.subscriptionmembership_set.all()
        })
        # member2 has no access
        self.assertGet(reverse('manage-sub-recent'), member=self.member2, code=403)


@tag('shares')
class ManageSubSharesTests(JuntagricoTestCaseWithShares):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Share.objects.create(member=cls.member2)  # add unpaid share

    def testSubscriptionSharesList(self):
        self.assertGet(reverse('manage-sub-shares'))
        self.assertGet(reverse('manage-sub-shares'), member=self.admin)
        # member 2 has no access
        self.assertGet(reverse('manage-sub-pending'), member=self.member2, code=403)
