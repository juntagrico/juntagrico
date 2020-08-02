from django.urls import reverse

from test.util.test import JuntagricoTestCase


class MailerTests(JuntagricoTestCase):

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
