from django.core.exceptions import ValidationError
from django.urls import reverse

from juntagrico.entity.share import Share
from test.util.test import JuntagricoTestCase


class SubscriptionTests(JuntagricoTestCase):

    def testSub(self):
        self.assertGet(reverse('sub-detail'))
        self.assertGet(reverse('sub-detail-id', args=[self.sub.pk]))

    def testSubActivation(self):
        self.assertGet(reverse('sub-activate', args=[self.sub2.pk]), 302)
        self.member2.refresh_from_db()
        self.assertIsNone(self.member2.subscription_future)
        self.assertEqual(self.member2.subscription_current, self.sub2)

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

    def testDepotChange(self):
        self.assertGet(reverse('depot-change', args=[self.sub.pk]))
        self.assertPost(reverse('depot-change', args=[self.sub.pk]), {'depot': self.depot2.pk})
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.future_depot, self.depot2)

    def testDepotChangeWaiting(self):
        self.assertPost(reverse('depot-change', args=[self.sub2.pk]), {'depot': self.depot2.pk}, member=self.member2)
        self.sub2.refresh_from_db()
        self.assertEqual(self.sub2.depot, self.depot2)
        self.assertIsNone(self.sub2.future_depot)

    def testDepot(self):
        self.assertGet(reverse('depot', args=[self.sub.depot.pk]))

    def testNicknameChange(self):
        test_nickname = 'My Nickname'
        self.assertGet(reverse('nickname-change', args=[self.sub.pk]))
        self.assertPost(reverse('nickname-change', args=[self.sub.pk]), {'nickname': test_nickname}, 302)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.nickname, test_nickname)

    def testSizeChange(self):
        with self.settings(BUSINESS_YEAR_CANCELATION_MONTH=12):
            self.assertGet(reverse('size-change', args=[self.sub.pk]))
            post_data = {
                'amount[' + str(self.sub_type.pk) + ']': 0,
                'amount[' + str(self.sub_type2.pk) + ']': 1
            }
            self.assertPost(reverse('size-change', args=[self.sub.pk]), post_data)
            self.sub.refresh_from_db()
            self.assertEqual(self.sub.future_parts.all()[0].type, self.sub_type)
            self.assertEqual(self.sub.future_parts.count(), 1)
            Share.objects.create(**self.share_data)
            self.assertGet(reverse('part-cancel', args=[self.sub.parts.all()[0].id, self.sub.pk]), code=302)
            self.assertPost(reverse('size-change', args=[self.sub.pk]), post_data, code=302)
            self.sub.refresh_from_db()
            self.assertEqual(self.sub.future_parts.all()[0].type, self.sub_type2)
            self.assertEqual(self.sub.future_parts.count(), 1)

    def testLeave(self):
        self.assertGet(reverse('sub-leave', args=[self.sub.pk]), 302, self.member3)
        Share.objects.create(**self.get_share_data(self.member3))
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
        Share.objects.create(**self.get_share_data(self.member4))
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

    def testSubDeActivation(self):
        self.assertGet(reverse('sub-activate', args=[self.sub2.pk]), 302)
        self.assertGet(reverse('extra-activate', args=[self.esub.pk]), 302)
        self.assertGet(reverse('extra-activate', args=[self.esub2.pk]), 302)
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
