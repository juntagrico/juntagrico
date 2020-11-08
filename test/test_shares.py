from django.urls import reverse
from django.utils import timezone

from test.util.test import JuntagricoTestCase


class ShareTests(JuntagricoTestCase):

    def testShareManage(self):
        self.assertGet(reverse('manage-shares'), 200)
        self.assertPost(reverse('manage-shares'), {'shares': 0}, 200, member=self.member2)
        self.member2.refresh_from_db()
        self.assertEqual(self.member2.share_set.count(), 0)
        self.assertPost(reverse('manage-shares'), {'shares': 1}, 302, member=self.member2)
        self.member2.refresh_from_db()
        self.assertEqual(self.member2.share_set.count(), 1)

    def testShareCancel(self):
        share = self.member.share_set.first()
        self.assertGet(reverse('share-cancel', args=[share.pk]), 302)

    def testSharePayout(self):
        share = self.member.share_set.first()
        share.cancelled_date = timezone.now().date()
        share.termination_date = timezone.now().date()
        share.save()
        self.assertGet(reverse('share-payout', args=[share.pk]), 302)
        self.assertEqual(self.member2.active_shares.count(), 0)
