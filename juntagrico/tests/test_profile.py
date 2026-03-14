from django.conf import settings
from django.contrib.auth.models import Permission
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from . import JuntagricoTestCase


class ProfileTests(JuntagricoTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = cls.create_member('member_with_shares@email.org', True)
        cls.member.number = 1
        cls.member.save()
        cls.membership = cls.member.memberships.first()
        cls.default_member = cls.member
        cls.member_without_shares = cls.create_member('member_without_shares@email.org')
        cls.member_with_unpaid_share = cls.create_member('member_with_unpaid_share@email.org')
        cls.member_with_canceled_share = cls.create_member('member_with_canceled_share@email.org')
        if settings.ENABLE_SHARES:
            cls.paid_share = cls.create_paid_share(cls.member)
            cls.unpaid_share = Share.objects.create(member=cls.member_with_unpaid_share)
            cls.canceled_share = cls.create_paid_and_canceled_share(cls.member_with_canceled_share)
        cls.admin = Member.objects.get(email='admin@email.org')
        cls.admin.user.user_permissions.add(
            Permission.objects.get(codename='notified_on_member_cancellation')
        )
        cls.cancellation_data = {
            'message': 'my last message',
            'iban': 'CH61 0900 0000 1900 0012 6',
            'addr_street': 'addr_street',
            'addr_zipcode': ' 1234',
            'addr_location': 'addr_location'
        }

    @override_settings(MEMBERSHIP={'enable': False})
    def testProfileNoMemberships(self):
        self.assertGet(reverse('profile'))

    def testProfileWithRequestedMembership(self):
        self.membership.activation_date = None
        self.membership.save()
        self.assertGet(reverse('profile'))

    def testProfileWithActiveMembership(self):
        self.assertGet(reverse('profile'))

    def testProfileWithCanceledMembership(self):
        self.membership.cancellation_date = '2026-03-12'
        self.membership.save()
        self.assertGet(reverse('profile'))

    def testProfileWithoutMembership(self):
        self.membership.deactivation_date = self.membership.cancellation_date = '2026-03-12'
        self.membership.save()
        self.assertGet(reverse('profile'))

    def testProfilePost(self):
        self.assertPost(reverse('profile'), {'iban': 'CH29 0900 0000 9000 1480 3',
                                             'email': 'test@juntagrico.org',
                                             'addr_street': 'addr_street',
                                             'addr_zipcode': ' 1234',
                                             'addr_location': 'addr_location',
                                             'phone': 'phone'})


class AuthTests(JuntagricoTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.deactivated_member = cls.create_member('deactivated_member@example.com', deactivation_date='2020-01-01')

    def testConfirmEmail(self):
        self.assertGet(reverse('send-confirm'))
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(ENFORCE_MAIL_CONFIRMATION=False)
    def testUnconfirmedLogin(self):
        # login with unconfirmed email passes
        self.assertEqual(self.member.confirmed, False)
        response = self.client.post(reverse('login'), {
            'username': self.member.email,
            'password': self.member.set_password(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def testConfirm(self):
        # after creation confirmed must be false
        self.assertEqual(self.member.confirmed, False)
        # login with unconfirmed email should fail and send confirmation email
        response = self.client.post(reverse('login'), {
            'username': self.member.email,
            'password': self.member.set_password(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        # changing email should reset confirmation
        self.member.confirmed = True
        self.member.save()
        self.assertEqual(self.member.confirmed, True)
        self.member.email = 'new_email@email.org'
        self.member.save()
        self.assertEqual(self.member.confirmed, False)
        # test confirmation link
        response = self.client.get(reverse('confirm', args=['wrong_hash']))
        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertEqual(self.member.confirmed, False)
        response = self.client.get(reverse('confirm', args=[self.member.get_hash()]))
        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertEqual(self.member.confirmed, True)

    def testChangePassword(self):
        self.assertGet(reverse('password'))

    def testChangePasswordPost(self):
        self.assertPost(reverse('password'), {'password': 'password',
                                              'passwordRepeat': 'password'})

    def testNewPassword(self):
        self.assertGet(reverse('password_reset'))
        self.assertEqual(len(mail.outbox), 0)

    def testNewPasswordPost(self):
        self.assertPost(reverse('password_reset'), {'email': 'email1@email.org'}, code=302)
        self.assertEqual(len(mail.outbox), 1)

    def testDeactivatedMemberNewPasswordPost(self):
        self.assertPost(reverse('password_reset'), {'email': 'deactivated_member@example.com'}, code=302)
        self.assertEqual(len(mail.outbox), 0)  # should send no email

    def testLogout(self):
        self.assertGet(reverse('logout'), code=302)
