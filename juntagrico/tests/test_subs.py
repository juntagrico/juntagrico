import datetime

from django.core.exceptions import ValidationError
from django.urls import reverse

from . import JuntagricoTestCase


class SubscriptionTests(JuntagricoTestCase):
    fixtures = JuntagricoTestCase.fixtures + ['test/shares']

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
        with self.settings(BUSINESS_YEAR_CANCELATION_MONTH=12):
            # order a type2 part, but with insufficient shares. Should fail, i.e., not change anything
            self.assertGet(reverse('part-order', args=[self.sub.pk]))
            post_data = {
                'amount[' + str(self.sub_type.pk) + ']': 0,
                'amount[' + str(self.sub_type2.pk) + ']': 1
            }
            self.assertPost(reverse('part-order', args=[self.sub.pk]), post_data)
            self.sub.refresh_from_db()
            self.assertEqual(self.sub.future_parts.all()[0].type, self.sub_type)
            self.assertEqual(self.sub.future_parts.count(), 1)
            # Add a share and cancel an existing part. Then order a part that requires 2 shares. Should succeed.
            self.create_paid_share(self.member)
            self.assertGet(reverse('part-cancel', args=[self.sub.parts.all()[0].id, self.sub.pk]), code=302)
            self.assertPost(reverse('part-order', args=[self.sub.pk]), post_data, code=302)
            self.sub.refresh_from_db()
            self.assertEqual(self.sub.future_parts.all()[0].type, self.sub_type2)
            self.assertEqual(self.sub.future_parts.count(), 1)

    def testTypeChange(self):
        # change type, with unsufficient shares
        part = self.sub.parts.all()[0]
        self.assertGet(reverse('part-change', args=[part.pk]))
        post_data = {'part_type': self.sub_type2.pk}
        self.assertPost(reverse('part-change', args=[part.pk]), post_data)
        self.sub.refresh_from_db()
        # check: type and amount unchanged
        self.assertEqual(self.sub.future_parts.count(), 1)
        self.assertEqual(self.sub.future_parts.all()[0].type, self.sub_type)

        # add a shares for type2
        self.create_paid_share(self.member)
        # change active type
        part = self.sub.parts.all()[0]
        self.assertGet(reverse('part-change', args=[part.pk]))
        post_data = {'part_type': self.sub_type2.pk}
        self.assertPost(reverse('part-change', args=[part.pk]), post_data, code=302)
        self.sub.refresh_from_db()
        # check: has only one uncancelled part with new type
        self.assertEqual(self.sub.future_parts.count(), 1)
        self.assertEqual(self.sub.future_parts.all()[0].type, self.sub_type2)
        # check: previous part was cancelled
        part.refresh_from_db()
        self.assertTrue(part.canceled)

        # change future type
        part = self.sub.future_parts.all()[0]
        post_data = {'part_type': self.sub_type.pk}
        self.assertPost(reverse('part-change', args=[part.pk]), post_data, code=302)
        self.sub.refresh_from_db()
        # check: has only one uncancelled part with first type
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
        self.assertGet(reverse('sub-leave', args=[self.sub.pk]), 302, self.member3)
        self.create_paid_share(self.member3)
        self.assertGet(reverse('sub-leave', args=[self.sub.pk]), member=self.member3)
        self.assertPost(reverse('sub-leave', args=[self.sub.pk]), code=302, member=self.member3)
        self.sub.refresh_from_db()
        self.assertEqual(len(self.sub.recipients), 1)

    def testJoin(self):
        self.assertGet(reverse('add-member', args=[self.sub.pk]), member=self.member)
        self.assertPost(reverse('add-member', args=[self.sub.pk]), member=self.member,
                        data={'email': self.member4.email})

    def testJoinLeaveRejoin(self):
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
        self.assertEqual(len(self.sub.recipients), 3)

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
