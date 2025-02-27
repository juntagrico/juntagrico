import datetime

from django.core import mail
from django.test import tag
from django.urls import reverse

from . import JuntagricoTestCase


@tag('shares')
class ShareTests(JuntagricoTestCase):
    fixtures = JuntagricoTestCase.fixtures + ['test/shares']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_paid_share(cls.member)
        mail.outbox.clear()

    def testShareManage(self):
        self.assertGet(reverse('manage-shares'), 200)
        self.assertPost(reverse('manage-shares'), {'shares': 0}, 200, member=self.member2)
        self.member2.refresh_from_db()
        self.assertEqual(self.member2.share_set.count(), 0)
        self.assertPost(reverse('manage-shares'), {'shares': 1}, 302, member=self.member2)
        self.member2.refresh_from_db()
        self.assertEqual(self.member2.share_set.count(), 1)

    def testShareCancel(self):
        share = self.member.share_set.last()
        today = datetime.date.today()
        self.assertGet(reverse('share-cancel', args=[share.pk]), 302)
        share.refresh_from_db()
        self.assertEqual(share.cancelled_date, today)
        self.assertNotEqual(share.termination_date, None)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['email1@email.org'])

    def testCancelWrongShare(self):
        # should fail
        share = self.member4.share_set.first()
        self.assertGet(reverse('share-cancel', args=[share.pk]), 404)
        share.refresh_from_db()
        self.assertEqual(share.cancelled_date, None)
        self.assertEqual(share.termination_date, None)

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
