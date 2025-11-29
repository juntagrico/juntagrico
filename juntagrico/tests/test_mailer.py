from unittest.mock import patch

from django.conf import settings
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


class AreaMailerTests(JuntagricoTestCaseWithShares):
    def testSending(self):
        url = reverse('email-to-area', args=[self.area.id])
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

    def testRecipientCounter(self):
        response = self.assertGet(reverse('email-count-area-recipients', args=[self.area.id]), data={
            'to_area': 'on'
        })
        self.assertEqual(b'An 1 Person senden', response.content)


class AreaCoordinatorMailerTests(AreaMailerTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_member = cls.area_admin_contact

    def testNoAccess(self):
        # no access to other area
        self.assertGet(reverse('email-to-area', args=[self.area2.id]), 403)
        # no access for area coordinator that can't contact
        self.assertGet(reverse('email-to-area', args=[self.area.id]), 403, member=self.area_admin_viewer)


class JobMailerTests(JuntagricoTestCaseWithShares):
    def testSending(self):
        url = reverse('email-to-job', args=[self.job2.id])
        self.assertGet(url)
        self.assertPost(url)
        self.assertEqual(len(mail.outbox), 0)
        self.assertPost(url, {
            'from_email': 'private',
            'to_job': 'on',
            'subject': 'Test',
            'body': 'Test Body',
            'submit': 1
        }, 302)
        self.assertEqual(len(mail.outbox), 1)

    def testRecipientCounter(self):
        response = self.assertGet(reverse('email-count-job-recipients', args=[self.job2.id]), data={
            'to_job': 'on'
        })
        self.assertEqual(b'An 1 Person senden', response.content)


class JobCoordinatorMailerTests(JobMailerTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_member = cls.area_admin_contact

    def testNoAccess(self):
        # no access to other area jobs
        self.assertGet(reverse('email-to-job', args=[self.past_core_job.id]), 403)
        # no access for area coordinator that can't contact
        self.assertGet(reverse('email-to-job', args=[self.job1.id]), 403, member=self.area_admin_viewer)


class DepotMailerTests(JuntagricoTestCaseWithShares):
    def testSending(self):
        url = reverse('email-to-depot', args=[self.depot.id])
        self.assertGet(url)
        self.assertPost(url)
        self.assertEqual(len(mail.outbox), 0)
        self.assertPost(url, {
            'from_email': 'private',
            'to_depot': 'on',
            'subject': 'Test',
            'body': 'Test Body',
            'submit': 1
        }, 302)
        self.assertEqual(len(mail.outbox), 1)

    def testRecipientCounter(self):
        response = self.assertGet(reverse('email-count-depot-recipients', args=[self.depot.id]), data={
            'to_depot': 'on'
        })
        self.assertEqual(b'An 3 Personen senden', response.content)


class DepotCoordinatorMailerTests(DepotMailerTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_member = cls.depot_coordinator

    def testNoAccess(self):
        # no access to other depots
        self.assertGet(reverse('email-to-depot', args=[self.depot2.id]), 403)


class MemberMailerTests(JuntagricoTestCaseWithShares):
    def _testSending(self, sender, to_member):
        url = reverse('email-to-member', args=[to_member.id])
        self.assertGet(url, member=sender)
        self.assertPost(url, member=sender)
        self.assertEqual(len(mail.outbox), 0)
        self.assertPost(url, {
            'from_email': 'private',
            'to_members': [to_member.id],
            'subject': 'Test',
            'body': 'Test Body',
            'submit': 1
        }, 302, member=sender)
        self.assertEqual(len(mail.outbox), 1)

    def testSendingWithPermission(self):
        self._testSending(self.member, self.member2)

    def testSendingByAreaAdmin(self):
        # can contact member in area
        self._testSending(self.area_admin_contact, self.member)
        # can contact members that are contactable in general
        mail.outbox = []
        self._testSending(self.area_admin_contact, self.member6)

    def testSendingByDepotAdmin(self):
        # can contact member in depot
        self._testSending(self.depot_coordinator, self.member3)
        # can contact members that are contactable in general
        mail.outbox = []
        self._testSending(self.depot_coordinator, self.member6)

    def testCantContact(self):
        # can't contact inactive member
        self.assertFalse(self.member.can_contact(self.inactive_member))
        self.assertGet(reverse('email-to-member', args=[self.inactive_member.id]), 403)
        # area admin can't contact members outside of area
        self.assertFalse(self.area_admin_contact.can_contact(self.member2))
        # depot admin can't contact members outside of depot
        self.assertFalse(self.depot_coordinator.can_contact(self.member2))


class MailerTests(JuntagricoTestCaseWithShares):
    def testMailer(self):
        # test access
        self.assertGet(reverse('email-write'))
        self.assertGet(reverse('email-write'), member=self.area_admin_contact)
        self.assertGet(reverse('email-write'), member=self.depot_coordinator)
        # test no access
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
                'to_list': ['all_subscriptions'],
                'to_members': [self.member.id],
                'to_areas': [self.area.id],
                'to_depots': [self.depot.id],
                'to_job': [self.job2.id],
                'copy': 'on',
                'subject': 'test',
                'attachments0': fp
            }
            if settings.ENABLE_SHARES:
                post_data['to_list'].append('all_shares')
            response = self.assertPost(reverse('email-write'), post_data, code=302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].attachments[0][0], 'test_mailer.py')
        self.assertListEqual(sorted(mail.outbox[0].bcc), [
            'First_name4 Last_name4 <email4@email.org>',
            'first_name1 last_name1 <email1@email.org>',
            'first_name3 last_name3 <email3@email.org>',
            'first_name6 last_name6 <member6@email.org>'
        ])
        self.assertRedirects(response, reverse('email-sent'))

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

    def testMailTemplate(self):
        self.assertGet(reverse('email-template', args=[self.mail_template.pk]))
        self.assertGet(reverse('email-template', args=[self.mail_template.pk]), member=self.member2, code=302)

    @override_settings(EMAIL_BACKEND='juntagrico.backends.email.LocmemBatchEmailBackend')
    @patch('juntagrico.backends.email.LocmemBatchEmailBackend.send_messages', mock_batch_mailer)
    def testBatchMailer(self):
        post_data = {
            'from_email': 'private',
            'to_list': ['all_subscriptions'],
            'to_members': [1],
            'subject': 'test',
        }
        if settings.ENABLE_SHARES:
            post_data['to_list'].append('all_shares')
        self.assertPost(reverse('email-write'), post_data, code=302)
        # check that email was split into batches
        self.assertEqual(len(mail.outbox), 7 if settings.ENABLE_SHARES else 6)
