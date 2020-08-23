from django.core import mail
from django.urls import reverse
from django.utils import timezone

from test.util.test import JuntagricoTestCase


class ProfileTests(JuntagricoTestCase):

    def testProfile(self):
        self.assertGet(reverse('profile'))

    def testProfilePost(self):
        self.assertPost(reverse('profile'), {'iban': 'CH29 0900 0000 9000 1480 3',
                                             'email': 'test@juntagrico.org',
                                             'addr_street': 'addr_street',
                                             'addr_zipcode': ' 1234',
                                             'addr_location': 'addr_location',
                                             'phone': 'phone'})

    def testCancelMembership(self):
        self.assertGet(reverse('cancel-membership'))

    def testCancelMembershipPost(self):
        self.assertPost(reverse('cancel-membership'), code=302)

    def testCancelMembershipNonCoopPost(self):
        self.assertPost(reverse('cancel-membership'), code=302, member=self.member3)
        self.member3.refresh_from_db()
        self.assertTrue(self.member3.inactive)

    def testDeactivateMembership(self):
        # must first cancel and pay back the shares
        for share in self.member.active_shares:
            share.cancelled_date = timezone.now().date()
            share.termination_date = timezone.now().date()
            share.payback_date = timezone.now().date()
            share.save()
        # and delete the subscription
        self.member.subscription_current.delete()
        self.assertPost(reverse('member-deactivate', args=(self.member.pk,)), code=302)
        self.member.refresh_from_db()
        self.assertTrue(self.member.inactive)

    def testConfirmEmail(self):
        self.assertGet(reverse('send-confirm'))
        self.assertEqual(len(mail.outbox), 1)

    def testChangePassword(self):
        self.assertGet(reverse('password'))

    def testChangePasswordPost(self):
        self.assertPost(reverse('password'), {'password': 'password',
                                              'passwordRepeat': 'password'})

    def testNewPassword(self):
        self.assertGet(reverse('new-password'))
        self.assertEqual(len(mail.outbox), 0)

    def testNewPasswordPost(self):
        self.assertPost(reverse('new-password'), {'username': 'email3@email.org'})
        self.assertEqual(len(mail.outbox), 1)

    def testLogout(self):
        self.assertGet(reverse('logout'), code=302)
