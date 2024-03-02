from django.core import mail
from django.urls import reverse

from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from . import JuntagricoTestCase


class ProfileTests(JuntagricoTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = cls.create_member('member_with_shares@email.org')
        cls.paid_share = cls.create_paid_share(cls.member)
        cls.member_without_shares = cls.create_member('member_without_shares@email.org')
        cls.member_with_unpaid_share = cls.create_member('member_with_unpaid_share@email.org')
        cls.unpaid_share = Share.objects.create(member=cls.member_with_unpaid_share)
        cls.member_with_cancelled_share = cls.create_member('member_with_cancelled_share@email.org')
        cls.cancelled_share = cls.create_paid_and_cancelled_share(cls.member_with_cancelled_share)
        cls.admin = Member.objects.get(email='admin@email.org')

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
        data = {
            'message': 'message',
            'iban': 'CH61 0900 0000 1900 0012 6',
            'addr_street': 'addr_street',
            'addr_zipcode': ' 1234',
            'addr_location': 'addr_location'
        }
        self.assertPost(reverse('cancel-membership'), code=302, data=data)
        self.member.refresh_from_db()
        self.assertTrue(self.member.canceled)
        self.assertEqual(self.member.usable_shares_count, 0)
        # pay back the share
        self.paid_share.refresh_from_db()
        self.paid_share.payback_date = self.paid_share.termination_date
        self.paid_share.save()
        # deactivate member
        self._testDeactivateMembership(self.member)

    def testCancelMembershipPostWithUnpaidShares(self):
        data = {
            'message': 'message',
            'iban': 'CH61 0900 0000 1900 0012 6',
            'addr_street': 'addr_street',
            'addr_zipcode': ' 1234',
            'addr_location': 'addr_location'
        }
        self.assertPost(reverse('cancel-membership'), code=302, member=self.member_with_unpaid_share, data=data)
        self.member_with_unpaid_share.refresh_from_db()
        self.assertTrue(self.member_with_unpaid_share.canceled)
        self.assertEqual(self.member_with_unpaid_share.usable_shares_count, 0)
        self._testDeactivateMembership(self.member_with_unpaid_share)

    def testCancelMembershipNonCoopPost(self):
        data = {
            'message': 'message',
            'iban': ''
        }
        self.assertPost(reverse('cancel-membership'), code=302, member=self.member_without_shares, data=data)
        self.member_without_shares.refresh_from_db()
        self.assertTrue(self.member_without_shares.inactive)
        self._testDeactivateMembership(self.member_without_shares)

    def testCancelMembershipWithCancelledShares(self):
        self.assertPost(reverse('cancel-membership'), code=302, member=self.member_with_cancelled_share)
        self.member_with_cancelled_share.refresh_from_db()
        self.assertTrue(self.member_with_cancelled_share.canceled)
        # pay back the share
        self.cancelled_share.refresh_from_db()
        self.cancelled_share.payback_date = self.cancelled_share.termination_date
        self.cancelled_share.save()
        self._testDeactivateMembership(self.member_with_cancelled_share)

    def _testDeactivateMembership(self, member):
        self.assertPost(reverse('member-deactivate', args=(member.pk,)), member=self.admin, code=302)
        member.refresh_from_db()
        self.assertTrue(member.inactive)

    def testConfirmEmail(self):
        self.assertGet(reverse('send-confirm'))
        self.assertEqual(len(mail.outbox), 1)

    def testChangePassword(self):
        self.assertGet(reverse('password'))

    def testChangePasswordPost(self):
        self.assertPost(reverse('password'), {'password': 'password',
                                              'passwordRepeat': 'password'})

    def testNewPassword(self):
        self.assertGet(reverse('password_reset'))
        self.assertEqual(len(mail.outbox), 0)

    def testNewPasswordPost(self):
        self.assertPost(reverse('password_reset'), {'email': 'member_without_shares@email.org'}, code=302)
        self.assertEqual(len(mail.outbox), 1)

    def testLogout(self):
        self.assertGet(reverse('logout'), code=302)
