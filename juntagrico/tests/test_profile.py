import hashlib

from django.conf import settings
from django.contrib.auth import get_user
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
        cls.deactivated_member = cls.create_member(
            'deactivated_member@example.com',
            deactivation_date='2020-01-01',
            confirmed=True,
        )

    def testConfirmEmail(self):
        self.assertGet(reverse('send-confirm'))
        self.assertEqual(len(mail.outbox), 1)

    def testLoginWithEmail(self):
        self.member.confirmed = True
        self.member.save()
        response = self.client.post(reverse('login'), {
            'username': self.member.email,
            'password': self.member.set_password(),
        })
        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def testLoginWithUsername(self):
        self.member.confirmed = True
        self.member.save()
        response = self.client.post(reverse('login'), {
            'username': self.member.user.username,
            'password': self.member.set_password(),
        })
        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

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
        token_before_change = Member.objects.get(pk=self.member.pk).get_hash()
        self.member.email = 'other_email@email.org'
        self.member.save()
        # the former unsigned hash can be computed by anyone
        old_hash = hashlib.sha1((str(self.member.email) + str(self.member.pk)).encode('utf8')).hexdigest()
        for invalid in ['wrong_hash', old_hash, token_before_change, self.member.get_hash() + 'x']:
            response = self.client.get(reverse('confirm', args=[invalid]))
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response.context['error_message'])
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

    def testDeactivatedUserSessionEnds(self):
        self.client.force_login(self.member.user, 'juntagrico.util.auth.AuthenticateWithEmail')
        self.assertEqual(self.client.get(reverse('profile')).status_code, 200)
        self.member.user.is_active = False
        self.member.user.save()
        self.assertEqual(self.client.get(reverse('profile')).status_code, 302)

    def testDeactivatedMemberSessionEnds(self):
        self.client.force_login(self.deactivated_member.user, 'juntagrico.util.auth.AuthenticateWithEmail')
        self.assertEqual(self.client.get(reverse('profile')).status_code, 302)

    def testInactiveUserLogin(self):
        self.member.user.is_active = False
        self.member.user.save()
        self.member.confirmed = True
        self.member.save()
        response = self.client.post(reverse('login'), {
            'username': self.member.email,
            'password': self.member.set_password(),
        })
        self.assertEqual(response.status_code, 200)
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
    def testInactiveMemberLogin(self):
        # The AuthenticateWithEmail backend will show a generic error message
        # because deactivated members are excluded earlier
        # In case another backend is used, the login form will also fail with a more specific error message
        response = self.client.post(
            reverse('login'),
            {
                'username': self.deactivated_member.user.username,
                'password': self.deactivated_member.set_password(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dein Konto ist deaktiviert')
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def testLogout(self):
        self.assertGet(reverse('logout'), code=405)
        self.assertPost(reverse('logout'), code=302)
