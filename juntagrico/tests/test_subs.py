import datetime

from django.conf import settings
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import tag
from django.urls import reverse

from . import JuntagricoTestCaseWithShares
from ..entity.member import SubscriptionMembership
from ..entity.subtypes import SubscriptionType


class SubscriptionTests(JuntagricoTestCaseWithShares):
    def testSub(self):
        self.assertGet(reverse('subscription-landing'), 302)
        self.assertGet(reverse('subscription-single', args=[self.sub.pk]))

    def testSubActivation(self):
        self.assertGet(reverse('sub-activate', args=[self.sub2.pk]), 302)
        self.member2.refresh_from_db()
        self.area.refresh_from_db()
        self.assertIsNone(self.member2.subscription_future)
        self.assertEqual(self.member2.subscription_current, self.sub2)
        self.assertTrue(self.member2 in self.area.members.all())

    def testSubChange(self):
        self.assertGet(reverse('sub-change', args=[self.sub.pk]))

    def testPrimaryChange(self):
        self.assertGet(reverse('primary-change', args=[self.sub.pk]))
        self.assertPost(reverse('primary-change', args=[self.sub.pk]), {'primary': self.member3.pk}, 302)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.primary_member.id, self.member3.id)

    def testPrimaryChangeError(self):
        with self.assertRaises(ValidationError):
            self.assertPost(reverse('primary-change', args=[self.sub.pk]), {'primary': self.member2.pk}, 500)

    def testDepot(self):
        self.assertGet(reverse('depot', args=[self.sub.depot.pk]))
        self.assertGet(reverse('depot-landing'))

    def testNicknameChange(self):
        test_nickname = 'My Nickname'
        self.assertGet(reverse('nickname-change', args=[self.sub.pk]))
        self.assertPost(reverse('nickname-change', args=[self.sub.pk]), {'nickname': test_nickname}, 302)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.nickname, test_nickname)

    def testPartOrder(self):
        with (self.settings(BUSINESS_YEAR_CANCELATION_MONTH=12)):
            self.assertGet(reverse('part-order', args=[self.sub.pk]))
            post_data = {
                f'amount[{type_id}]': 1 if i == 1 else 0
                for i, type_id in enumerate(SubscriptionType.objects.order_by('id').values_list('id', flat=True))
            }
            # order a type2 part, but with insufficient shares. Should fail, i.e., not change anything
            if settings.ENABLE_SHARES:
                self.assertPost(reverse('part-order', args=[self.sub.pk]), post_data)
                self.sub.refresh_from_db()
                self.assertEqual(self.sub.future_parts.first().type, self.sub_type)
                self.assertEqual(self.sub.future_parts.count(), 1)
            # Add a share and cancel an existing part. Then order a part that requires 2 shares. Should succeed.
            self.create_paid_share(self.member)
            self.assertGet(reverse('part-cancel', args=[self.sub.parts.first().id, self.sub.pk]), code=302)
            self.assertPost(reverse('part-order', args=[self.sub.pk]), post_data, code=302)
            self.sub.refresh_from_db()
            self.assertEqual(self.sub.future_parts.first().type, self.sub_type2)
            self.assertEqual(self.sub.future_parts.count(), 1)

    @tag('shares')
    def testTypeChangeOnInsufficientShares(self):
        part = self.sub.parts.all()[0]
        self.assertGet(reverse('part-change', args=[part.pk]))
        post_data = {'part_type': self.sub_type2.pk}
        # should fail
        self.assertPost(reverse('part-change', args=[part.pk]), post_data)
        self.sub.refresh_from_db()
        # check: type and amount unchanged
        self.assertEqual(self.sub.future_parts.count(), 1)
        self.assertEqual(self.sub.future_parts.all()[0].type, self.sub_type)

    def testTypeChange(self):
        # add a shares for type2
        self.create_paid_share(self.member)
        mail.outbox.clear()
        # change active type
        part = self.sub.parts.all()[0]
        self.assertGet(reverse('part-change', args=[part.pk]))
        post_data = {'part_type': self.sub_type2.pk}
        self.assertPost(reverse('part-change', args=[part.pk]), post_data, code=302)
        self.sub.refresh_from_db()
        # check: has only one uncanceled part with new type
        self.assertEqual(self.sub.future_parts.count(), 1)
        self.assertEqual(self.sub.future_parts.all()[0].type, self.sub_type2)
        # check: previous part was canceled
        part.refresh_from_db()
        self.assertTrue(part.canceled)
        # check notification was sent to admins
        self.assertEqual(len(mail.outbox), 2)

        # change future type
        part = self.sub.future_parts.all()[0]
        post_data = {'part_type': self.sub_type.pk}
        self.assertPost(reverse('part-change', args=[part.pk]), post_data, code=302)
        self.sub.refresh_from_db()
        # check: has only one uncanceled part with first type
        self.assertEqual(self.sub.future_parts.count(), 1)
        self.assertEqual(self.sub.future_parts.all()[0].type, self.sub_type)

    def testCancelWaitingPart(self):
        with self.settings(BUSINESS_YEAR_CANCELATION_MONTH=12):
            # activate part with future date
            part = self.sub.parts.all()[0]
            part.activate(datetime.date.today() + datetime.timedelta(3))
            # should be able to cancel part today
            self.assertGet(reverse('part-cancel', args=[part.id, self.sub.pk]), code=302)
            self.sub.refresh_from_db()
            self.assertEqual(self.sub.future_parts.count(), 0)

    def testLeave(self):
        if settings.ENABLE_SHARES:
            self.assertGet(reverse('sub-leave', args=[self.sub.pk]), 302, self.member3)
            self.create_paid_share(self.member3)
        self.assertGet(reverse('sub-leave', args=[self.sub.pk]), member=self.member3)
        self.assertPost(reverse('sub-leave', args=[self.sub.pk]), code=302, member=self.member3)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.current_members.count(), 1)

    def testJoin(self):
        self.assertGet(reverse('add-member', args=[self.sub.pk]), member=self.member)
        self.assertPost(reverse('add-member', args=[self.sub.pk]), member=self.member,
                        data={'email': self.member4.email})

    def testJoinLeaveRejoin(self):
        # leaving on the same day should delete the subscription membership again
        post_data = {
            'email': self.member4.email,
            'first_name': self.member4.first_name,
            'last_name': self.member4.last_name,
            'addr_street': self.member4.addr_street,
            'addr_zipcode': '1234',
            'addr_location': self.member4.addr_location,
            'phone': self.member4.phone
        }
        self.create_paid_share(self.member4)
        self.assertPost(reverse('add-member', args=[self.sub.pk]), code=302, member=self.member, data=post_data)
        self.assertPost(reverse('sub-leave', args=[self.sub.pk]), code=302, member=self.member4)
        self.assertPost(reverse('add-member', args=[self.sub.pk]), code=302, member=self.member, data=post_data)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.current_members.count(), 3)

    def testRejoinPreviousSub(self):
        # rejoining on a later day should keep 2 subscription memberships
        today = datetime.date.today()
        a_while_ago = today - datetime.timedelta(days=10)
        old_sub = self.create_sub(self.depot, self.sub_type, activation_date=a_while_ago)
        SubscriptionMembership.objects.create(subscription=old_sub, member=self.member4, join_date=a_while_ago)
        self.member4.leave_subscription(changedate=datetime.date.today() - datetime.timedelta(days=5))
        self.assertEqual(old_sub.current_members.count(), 0)
        self.member4.join_subscription(old_sub)
        self.assertEqual(old_sub.current_members.count(), 1)
        self.assertEqual(old_sub.subscriptionmembership_set.count(), 2)
        # joining again should fail
        with self.assertRaises(ValidationError):
            self.member4.join_subscription(old_sub)
        with self.assertRaises(ValidationError):
            self.member4.join_subscription(self.sub)

    def testCancel(self):
        self.assertGet(reverse('sub-cancel', args=[self.sub.pk]), 200)
        self.assertPost(reverse('sub-cancel', args=[self.sub.pk]), code=302)
        self.sub.refresh_from_db()
        self.assertIsNotNone(self.sub.cancellation_date)

    def testCancelWaiting(self):
        self.assertGet(reverse('sub-cancel', args=[self.sub2.pk]), 200, member=self.member2)
        self.assertPost(reverse('sub-cancel', args=[self.sub2.pk]), code=302, member=self.member2)
        self.sub2.refresh_from_db()
        self.assertIsNotNone(self.sub2.cancellation_date)

    def testSubDeActivation(self):
        self.assertGet(reverse('sub-activate', args=[self.sub2.pk]), 302)
        self.assertGet(reverse('part-activate', args=[self.esub.pk]), 302)
        self.assertGet(reverse('part-activate', args=[self.esub2.pk]), 302)
        self.assertEqual(len(self.member2.subscriptions_old), 0)
        self.assertGet(reverse('sub-deactivate', args=[self.sub2.pk]), 302)
        self.member2.refresh_from_db()
        self.sub2.refresh_from_db()
        self.assertFalse(self.sub2.active)
        self.assertIsNone(self.member2.subscription_current)
        self.assertEqual(len(self.member2.subscriptions_old), 1)
        self.assertGet(reverse('sub-activate', args=[self.sub2.pk]), 302)
        self.sub2.refresh_from_db()
        self.assertFalse(self.sub2.active)

    def testFuture(self):
        self.assertGet(reverse('future'))
        self.assertGet(reverse('future'), member=self.member2, code=302)

    def testPrimaryMember(self):
        self.assertGet(reverse('sub-cancel', args=[self.sub.pk]), member=self.member3, code=302)

    def testMembers(self):
        self.assertListEqual(list(self.sub.current_members.order_by('id')), [self.member, self.member3])
