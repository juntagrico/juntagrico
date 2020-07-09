from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from juntagrico.entity.share import Share
from test.util.test import JuntagricoTestCase


class ShareTests(JuntagricoTestCase):

    def testShareOrder(self):
        self.assertGet(reverse('share-order'), 200)
        self.assertPost(reverse('share-order'), {'shares': 0}, 200, member=self.member2)
        self.member2.refresh_from_db()
        self.assertEqual(self.member2.share_set.count(), 0)
        self.assertPost(reverse('share-order'), {'shares': 1}, 302, member=self.member2)
        self.member2.refresh_from_db()
        self.assertEqual(self.member2.share_set.count(), 1)

    def testSharePayout(self):
        share = self.member.share_set.first()
        share.cancelled_date = timezone.now().date()
        share.termination_date = timezone.now().date()
        share.save()
        self.assertGet(reverse('share-payout', args=[share.pk]), 302)
        self.assertEqual(self.member2.active_shares.count(), 0)
