from django.conf import settings
from django.contrib.auth.models import Permission
from django.core import mail
from django.urls import reverse

from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from . import JuntagricoTestCase


class MembershipTests(JuntagricoTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = cls.create_member('member_with_shares@email.org', True)
        cls.default_member = cls.member
        cls.member_without_shares = cls.create_member('member_without_shares@email.org', True)
        cls.member_with_unpaid_share = cls.create_member('member_with_unpaid_share@email.org', True)
        cls.member_with_canceled_share = cls.create_member('member_with_canceled_share@email.org', True)
        if settings.ENABLE_SHARES:
            cls.paid_share = cls.create_paid_share(cls.member)
            cls.unpaid_share = Share.objects.create(member=cls.member_with_unpaid_share)
            cls.canceled_share = cls.create_paid_and_canceled_share(cls.member_with_canceled_share)
        cls.admin = Member.objects.get(email='admin@email.org')
        cls.admin.user.user_permissions.add(
            Permission.objects.get(codename='notified_on_membership_cancellation')
        )
        cls.cancellation_data = {
            'message': 'my last message',
            'iban': 'CH61 0900 0000 1900 0012 6',
            'addr_street': 'addr_street',
            'addr_zipcode': ' 1234',
            'addr_location': 'addr_location'
        }

    def testCancelMembership(self):
        self.assertGet(reverse('membership-cancel'))

    def testCancelMembershipPost(self):
        self.assertPost(reverse('membership-cancel'), code=302, data=self.cancellation_data)
        membership = self.member.memberships.first()
        self.assertTrue(membership.canceled)
        self.assertEqual(self.member.usable_shares_count, 0)
        # pay back the share
        if settings.ENABLE_SHARES:
            self.paid_share.refresh_from_db()
            self.paid_share.payback_date = self.paid_share.termination_date
            self.paid_share.save()
        # deactivate member
        self._testDeactivateMembership(membership)

    def testCancelMembershipPostWithUnpaidShares(self):
        self.assertPost(reverse('membership-cancel'), code=302, member=self.member_with_unpaid_share,
                        data=self.cancellation_data)
        self.assertEqual(len(mail.outbox), 1)  # admin notification
        self.assertTrue(self.cancellation_data['message'] in mail.outbox[0].body,
                        f'message not found in: {mail.outbox[0].body}')
        membership = self.member_with_unpaid_share.memberships.first()
        self.assertTrue(membership.canceled)
        self.assertEqual(self.member_with_unpaid_share.usable_shares_count, 0)
        self._testDeactivateMembership(membership)

    def testCancelMembershipNonCoopPost(self):
        data = {
            'message': 'a personal message',
        }
        self.assertPost(reverse('membership-cancel'), code=302, member=self.member_without_shares, data=data)
        self.assertEqual(len(mail.outbox), 1)  # admin notification
        self.assertTrue(data['message'] in mail.outbox[0].body, f'message not found in: {mail.outbox[0].body}')
        self.member_without_shares.refresh_from_db()
        membership = self.member_without_shares.memberships.first()
        self.assertTrue(membership.inactive)
        self._testDeactivateMembership(membership)

    def testCancelMembershipWithCanceledShares(self):
        self.assertPost(reverse('membership-cancel'), code=302, member=self.member_with_canceled_share)
        self.assertEqual(len(mail.outbox), 1)  # admin notification
        membership = self.member_with_canceled_share.memberships.first()
        self.assertTrue(membership.canceled)
        # pay back the share
        if settings.ENABLE_SHARES:
            self.canceled_share.refresh_from_db()
            self.canceled_share.payback_date = self.canceled_share.termination_date
            self.canceled_share.save()
        self._testDeactivateMembership(membership)

    def testCancelMembershipWithCanceledSubscriptions(self):
        self.set_up_depots()
        self.set_up_sub_types()
        sub = self.create_sub_now(self.depot)
        self.member.join_subscription(sub, True)
        # don't cancel while subscription is active
        self.assertPost(reverse('membership-cancel'), code=200, member=self.member, data=self.cancellation_data)
        self.member.refresh_from_db()
        self.assertFalse(self.member.canceled)
        self.assertEqual(len(mail.outbox), 0)
        # succeed when canceled
        sub.cancel()
        self.assertPost(reverse('membership-cancel'), code=302, member=self.member, data=self.cancellation_data)
        self.assertTrue(self.member.memberships.first().canceled)
        self.assertEqual(len(mail.outbox), 1)  # admin notification

    def _testDeactivateMembership(self, membership):
        # Expected result: members that have no paid shares, can be deactivated.
        self.assertPost(
            reverse('manage-membership-deactivate'),
            {'membership_ids': str(membership.pk)},
            member=self.admin,
            code=302
        )
        membership.refresh_from_db()
        self.assertTrue(membership.inactive, f'{membership.account} {membership.account.email}')

    def testDeactivateMembership(self):
        # Expected result: members that have no paid shares, can be deactivated.
        members = {
            self.member: not settings.ENABLE_SHARES,  # still has canceled shares
            self.member_without_shares: True,
            self.member_with_unpaid_share: True,
            self.member_with_canceled_share: not settings.ENABLE_SHARES
        }
        for member in members.keys():
            member.cancel()
        self.assertPost(
            reverse('manage-member-deactivate'),
            {'member_ids': '_'.join([str(m.pk) for m in members.keys()])},
            member=self.admin,
            code=302
        )
        for member, result in members.items():
            member.refresh_from_db()
            self.assertEqual(member.inactive, result, f'{member} {member.email}')
