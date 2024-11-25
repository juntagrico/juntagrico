from django.conf import settings
from django.core import mail
from django.urls import reverse

from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from . import JuntagricoTestCase


class ProfileTests(JuntagricoTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = cls.create_member('member_with_shares@email.org')
        cls.member_without_shares = cls.create_member('member_without_shares@email.org')
        cls.member_with_unpaid_share = cls.create_member('member_with_unpaid_share@email.org')
        cls.member_with_cancelled_share = cls.create_member('member_with_cancelled_share@email.org')
        if settings.ENABLE_SHARES:
            cls.paid_share = cls.create_paid_share(cls.member)
            cls.unpaid_share = Share.objects.create(member=cls.member_with_unpaid_share)
            cls.cancelled_share = cls.create_paid_and_cancelled_share(cls.member_with_cancelled_share)
        cls.admin = Member.objects.get(email='admin@email.org')
        cls.cancellation_data = {
            'message': 'message',
            'iban': 'CH61 0900 0000 1900 0012 6',
            'addr_street': 'addr_street',
            'addr_zipcode': ' 1234',
            'addr_location': 'addr_location'
        }

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
        self.assertPost(reverse('cancel-membership'), code=302, data=self.cancellation_data)
        self.member.refresh_from_db()
        self.assertTrue(self.member.canceled)
        self.assertEqual(self.member.usable_shares_count, 0)
        # pay back the share
        if settings.ENABLE_SHARES:
            self.paid_share.refresh_from_db()
            self.paid_share.payback_date = self.paid_share.termination_date
            self.paid_share.save()
        # deactivate member
        self._testDeactivateMembership(self.member)

    def testCancelMembershipPostWithUnpaidShares(self):
        self.assertPost(reverse('cancel-membership'), code=302, member=self.member_with_unpaid_share,
                        data=self.cancellation_data)
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
        if settings.ENABLE_SHARES:
            self.cancelled_share.refresh_from_db()
            self.cancelled_share.payback_date = self.cancelled_share.termination_date
            self.cancelled_share.save()
        self._testDeactivateMembership(self.member_with_cancelled_share)

    def testCancelMembershipWithCancelledSubscriptions(self):
        self.set_up_depots()
        sub = self.create_sub_now(self.depot)
        self.member.join_subscription(sub, True)
        # don't cancel while subscription is active
        self.assertPost(reverse('cancel-membership'), code=200, member=self.member, data=self.cancellation_data)
        self.member.refresh_from_db()
        self.assertFalse(self.member.canceled)
        # succeed when cancelled
        sub.cancel()
        self.assertPost(reverse('cancel-membership'), code=302, member=self.member, data=self.cancellation_data)
        self.member.refresh_from_db()
        self.assertTrue(self.member.canceled)

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
