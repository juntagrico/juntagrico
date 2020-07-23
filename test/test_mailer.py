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
        self.assertGet(reverse('mail-area'))
        self.assertGet(reverse('mail-area-send'), code=404)
        self.assertPost(reverse('mail-area-send'), code=302)
        self.assertGet(reverse('mail-area'), member=self.member2, code=302)

    def testMailDepot(self):
        self.assertGet(reverse('mail-depot'))
        self.assertGet(reverse('mail-depot-send'), code=404)
        self.assertPost(reverse('mail-depot-send'), code=302)
        self.assertGet(reverse('mail-depot'), member=self.member2, code=302)

    def testMailJob(self):
        self.assertGet(reverse('mail-job'))
        self.assertGet(reverse('mail-job-send'), code=404)
        self.assertPost(reverse('mail-job-send'), code=302)
        self.assertGet(reverse('mail-job'), member=self.member2, code=302)

    def testMailTemplate(self):
        self.assertGet(reverse('mail-template', args=[self.mail_template.pk]))
        self.assertGet(reverse('mail-template', args=[self.mail_template.pk]), member=self.member2, code=302)
