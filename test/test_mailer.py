from unittest.mock import patch

from django.core import mail
from django.urls import reverse

from test.util.test import JuntagricoTestCase
from django.test import override_settings


def mock_batch_mailer(msg):
    # patch batch mailer to not use threads to make it testable
    from juntagrico.util.mailer.batch import Mailer
    Mailer._send_batches(msg, 1, 0)  # testing with individual "to" emails
    Mailer._send_batches(msg, 2, 0)  # testing in batches of 2
    Mailer._send_batches(msg, 4, 3)  # testing with waiting time


class MailerTests(JuntagricoTestCase):
    fixtures = JuntagricoTestCase.fixtures + ['test/shares']

    def testMailer(self):
        self.assertGet(reverse('mail'))
        self.assertGet(reverse('mail'), member=self.member2, code=302)

    def testMailSend(self):
        with open('test/test_mailer.py') as fp:
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

    @override_settings(DEFAULT_MAILER='juntagrico.util.mailer.batch.Mailer')
    @patch('juntagrico.util.mailer.batch.Mailer.send', mock_batch_mailer)
    def testBatchMailer(self):
        post_data = {
            'sender': 'test@mail.org',
            'allsubscription': 'on',
            'allshares': 'on',
            'all': 'on',
            'recipients': 'test2@mail.org',
        }
        self.assertPost(reverse('mail-send'), post_data, code=302)
        self.assertEqual(len(mail.outbox), 14)  # check that email was split into batches
