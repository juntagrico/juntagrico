from django.core.exceptions import ValidationError
from django.urls import reverse

from juntagrico.entity.share import Share
from test.util.test import JuntagricoTestCase


class JobTests(JuntagricoTestCase):

    def testSub(self):
        self.assertGet(reverse('sub-detail'))
        self.assertGet(reverse('sub-detail-id', args=[self.sub.pk]))

    def testSubActivation(self):
        self.assertGet(reverse('sub-activate', args=[self.sub2.pk]), 302)
        self.member2.refresh_from_db()
        self.assertIsNone(self.member2.future_subscription)
        self.assertEqual(self.member2.subscription, self.sub2)

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

    def testSizeChange(self):
        with self.settings(BUSINESS_YEAR_CANCELATION_MONTH=12):
            self.assertGet(reverse('size-change', args=[self.sub.pk]))
            self.assertPost(reverse('size-change', args=[self.sub.pk]), {'amount[' + str(self.sub_type2.pk) + ']': 1})
            self.sub.refresh_from_db()
            self.assertEqual(self.sub.future_types.all()[0], self.sub_type)
            self.assertEqual(self.sub.future_types.count(), 1)
            Share.objects.create(**self.share_data)
            self.assertPost(reverse('size-change', args=[self.sub.pk]), {'amount[' + str(self.sub_type2.pk) + ']': 1})
            self.sub.refresh_from_db()
            self.assertEqual(self.sub.future_types.all()[0], self.sub_type2)
            self.assertEqual(self.sub.future_types.count(), 1)

    def testLeave(self):
        self.assertGet(reverse('sub-leave', args=[self.sub.pk]), 302, self.member3)
        Share.objects.create(**self.get_share_data(self.member3))
        self.assertGet(reverse('sub-leave', args=[self.sub.pk]), member=self.member3)
        self.assertPost(reverse('sub-leave', args=[self.sub.pk]), code=302, member=self.member3)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.recipients.count(), 1)

    def testSubDeActivation(self):
        self.assertGet(reverse('sub-activate', args=[self.sub2.pk]), 302)
        self.assertEqual(self.member2.old_subscriptions.count(), 0)
        self.assertGet(reverse('sub-deactivate', args=[self.sub2.pk]), 302)
        self.member2.refresh_from_db()
        self.assertIsNone(self.member2.subscription)
        self.assertEqual(self.member2.old_subscriptions.count(), 1)
        self.assertGet(reverse('sub-activate', args=[self.sub2.pk]), 302)
        self.sub2.refresh_from_db()
        self.assertFalse(self.sub2.active)
