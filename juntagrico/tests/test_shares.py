import datetime

from django.urls import reverse

from . import JuntagricoTestCase


class ShareTests(JuntagricoTestCase):
    fixtures = JuntagricoTestCase.fixtures + ['test/shares']

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
        share.cancelled_date = datetime.date.today()
        share.termination_date = datetime.date.today()
        share.save()
        self.assertGet(reverse('share-payout', args=[share.pk]), 302)
        self.assertEqual(self.member2.active_shares.count(), 0)

    def testShareCertificate(self):
        self.client.force_login(self.member.user)
        response = self.client.get(reverse('share-certificate') + '?year=2017')
        self.assertEqual(response['content-type'], 'application/pdf')
