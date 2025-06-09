from unittest.mock import patch

from django.core import mail
from django.test import override_settings, tag
from django.urls import reverse

from . import JuntagricoTestCaseWithShares


def mock_batch_mailer(self, msgs):
    # patch batch mailer to not use threads to make it testable
    for msg in msgs:
        self._send_batches(msg, 1, 0)  # testing with individual "to" emails
        self._send_batches(msg, 2, 0)  # testing in batches of 2
        self._send_batches(msg, 4, 3)  # testing with waiting time


class MailerTests(JuntagricoTestCaseWithShares):
    def testMailer(self):
        self.assertGet(reverse('mail'))
        self.assertGet(reverse('mail'), member=self.member2, code=302)

    def testMemberFromEmailSelection(self):
        self.assertListEqual(self.member.all_emails(), [('private', 'email1@email.org')])
        self.assertListEqual(self.member2.all_emails(), [
            ('general', 'info@juntagrico.juntagrico'), ('private', 'email2@email.org')
        ])
        self.assertListEqual(self.member3.all_emails(), [
            ('for_members', 'member@juntagrico.juntagrico'),
            ('for_subscriptions', 'subscription@juntagrico.juntagrico'),
            ('private', 'email3@email.org')
        ])
        self.assertListEqual(self.member4.all_emails(), [
            ('for_shares', 'share@juntagrico.juntagrico'), ('private', 'email4@email.org')
        ])
        self.assertListEqual(self.member5.all_emails(), [
            ('technical', 'it@juntagrico.juntagrico'), ('private', 'email5@email.org')
        ])
        self.assertListEqual(self.area_admin.all_emails(), [
            ('area1-m0', 'email_contact@example.org'),
            ('area2-m2', 'email2@email.org'),
            ('private', 'areaadmin@email.org')
        ])
        self.assertListEqual(self.admin.all_emails(), [
            ('general', 'info@juntagrico.juntagrico'),
            ('for_members', 'member@juntagrico.juntagrico'),
            ('for_subscriptions', 'subscription@juntagrico.juntagrico'),
            ('for_shares', 'share@juntagrico.juntagrico'),
            ('technical', 'it@juntagrico.juntagrico'),
            ('private', 'admin@email.org')
        ])

    def testMailSend(self):
        with open('juntagrico/tests/test_mailer.py') as fp:
            post_data = {
                'sender': 'test@mail.org',
                'allsubscription': 'on',
                'allshares': 'on',
                'all': 'on',
                'recipients': 'test2@mail.org',
                'allsingleemail': 'on',
                'singleemail': 'test3@mail.org test4@mail.org',
                'image-1': fp
            }
            self.assertGet(reverse('mail-send'), code=404)
            self.assertPost(reverse('mail-send'), post_data, code=302)

    @tag('shares')
    def testAllSharesMailSend(self):
        post_data = {
            'sender': 'test@mail.org',
            'allshares': 'on'
        }
        self.assertPost(reverse('mail-send'), post_data, code=302)
        self.assertListEqual(sorted(mail.outbox[0].bcc), ['email1@email.org', 'email4@email.org'])

    def testMailResult(self):
        self.assertGet(reverse('mail-result', args=[1]))

    def testMailArea(self):
        self.utilMailConcernTest('area')

    def testMailDepot(self):
        self.utilMailConcernTest('depot')

    def testMailJob(self):
        self.utilMailConcernTest('job')

    def testMailTemplate(self):
        self.assertGet(reverse('mail-template', args=[self.mail_template.pk]))
        self.assertGet(reverse('mail-template', args=[self.mail_template.pk]), member=self.member2, code=302)

    def utilMailConcernTest(self, concern):
        self.assertGet(reverse('mail-{}'.format(concern)))
        self.assertGet(reverse('mail-{}-send'.format(concern)), code=404)
        self.assertPost(reverse('mail-{}-send'.format(concern)), code=302)
        self.assertGet(reverse('mail-{}'.format(concern)), member=self.member2, code=302)

    @override_settings(EMAIL_BACKEND='juntagrico.backends.email.LocmemBatchEmailBackend')
    @patch('juntagrico.backends.email.LocmemBatchEmailBackend.send_messages', mock_batch_mailer)
    def testBatchMailer(self):
        post_data = {
            'sender': 'test@mail.org',
            'allsubscription': 'on',
            'allshares': 'on',
            'all': 'on',
            'recipients': 'test2@mail.org',
        }
        self.assertPost(reverse('mail-send'), post_data, code=302)
        self.assertEqual(len(mail.outbox), 17)  # check that email was split into batches
