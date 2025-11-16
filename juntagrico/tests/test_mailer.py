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
        return 1  # pretend message was sent


class MailerTests(JuntagricoTestCaseWithShares):
    def testMailer(self):
        self.assertGet(reverse('email-write'))
        self.assertGet(reverse('email-write'), member=self.member2, code=302)

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
        self.assertListEqual(self.area_admin_contact.all_emails(), [
            ('area1-m0', 'email_contact@example.org'),
            ('private', 'area_admin13@email.org')
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
                'from_email': 'private',
                'to_list': ['all_subscriptions', 'all_shares', 'all'],
                'to_members': [1],
                'subject': 'test',
                'attachment0': fp
            }
            self.assertPost(reverse('email-write'), post_data, code=302)
        self.assertEqual(len(mail.outbox), 1)

    @tag('shares')
    def testAllSharesMailSend(self):
        post_data = {
            'from_email': 'private',
            'to_list': ['all_shares'],
            'subject': 'test',
        }
        self.assertPost(reverse('email-write'), post_data, code=302)
        self.assertListEqual(sorted(mail.outbox[0].bcc), [
            'First_name4 Last_name4 <email4@email.org>',
            'first_name1 last_name1 <email1@email.org>'
        ])

    def testMailArea(self):
        url = reverse('email-to-area', args=[1])
        self.assertGet(url)
        self.assertPost(url)
        self.assertEqual(len(mail.outbox), 0)
        self.assertPost(url, {
            'from_email': 'private',
            'to_area': 'on',
            'subject': 'Test',
            'body': 'Test Body',
            'submit': 1
        }, 302)
        self.assertEqual(len(mail.outbox), 1)

    def testMailTemplate(self):
        self.assertGet(reverse('mail-template', args=[self.mail_template.pk]))
        self.assertGet(reverse('mail-template', args=[self.mail_template.pk]), member=self.member2, code=302)

    @override_settings(EMAIL_BACKEND='juntagrico.backends.email.LocmemBatchEmailBackend')
    @patch('juntagrico.backends.email.LocmemBatchEmailBackend.send_messages', mock_batch_mailer)
    def testBatchMailer(self):
        post_data = {
            'from_email': 'private',
            'to_list': ['all_subscriptions', 'all_shares', 'all'],
            'to_members': [1],
            'subject': 'test',
        }
        self.assertPost(reverse('email-write'), post_data, code=302)
        self.assertEqual(len(mail.outbox), 25)  # check that email was split into batches
