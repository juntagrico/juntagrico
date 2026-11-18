import datetime

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import override_settings, tag
from django.urls import reverse

from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.lifecycle.membership import sync
from . import JuntagricoTestCase
from ..entity.membership import Membership


class MembershipTests(JuntagricoTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = cls.create_member('member_with_shares@email.org', True)
        cls.default_member = cls.member
        cls.member_without_shares = cls.create_member('member_without_shares@email.org')
        cls.member_with_unpaid_share = cls.create_member('member_with_unpaid_share@email.org', True)
        cls.member_with_canceled_share = cls.create_member('member_with_canceled_share@email.org', True)
        cls.member_without_membership = cls.create_member('member_without_membership@email.org')
        if settings.ENABLE_SHARES:
            cls.paid_share = cls.create_paid_share(cls.member)
            cls.unpaid_share = Share.objects.create(member=cls.member_with_unpaid_share)
            cls.canceled_share = cls.create_paid_and_canceled_share(cls.member_with_canceled_share)
        cls.admin = Member.objects.get(email='admin@email.org')
        cls.admin.user.user_permissions.add(
            Permission.objects.get(codename='notified_on_membership_cancellation'),
            Permission.objects.get(codename='notified_on_membership_creation')
        )
        cls.cancellation_data = {
            'shares': 0,
            'membership': False,
            'account': True,
            'cancellation_comment': 'my last message',
            'iban': 'CH61 0900 0000 1900 0012 6',
            'addr_street': 'addr_street',
            'addr_zipcode': ' 1234',
            'addr_location': 'addr_location'
        }

    def testCreateMembership(self):
        self.assertGet(reverse('membership-create'), member=self.member_without_membership)
        creation_data = {'membership': True}
        if settings.ENABLE_SHARES:
            creation_data['of_member'] = 1
        self.assertPost(reverse('membership-create'), code=302, data=creation_data, member=self.member_without_membership)
        self.assertEqual(len(mail.outbox), 1 + 2 * settings.ENABLE_SHARES)  # admin notifications (2 share, 1 membership)
        mail.outbox = []
        self.assertEqual(self.member_without_membership.memberships.count(), 1)
        self.assertEqual(self.member_without_membership.share_set.count(), int(settings.ENABLE_SHARES))
        # repeating will not create another membership, but another share
        self.assertPost(reverse('membership-create'), code=302, data=creation_data, member=self.member_without_membership)
        self.assertEqual(len(mail.outbox), 1 + 2 * settings.ENABLE_SHARES)  # admin notifications (2 share, 1 membership)
        self.assertEqual(self.member_without_membership.memberships.count(), 1)
        self.assertEqual(self.member_without_membership.share_set.count(), int(settings.ENABLE_SHARES) * 2)

    @override_settings(BYLAWS='')
    def testCreateMembershipWithoutDocuments(self):
        self.assertGet(reverse('membership-create'), member=self.member_without_membership)

    def testCancelMembership(self):
        self.assertGet(reverse('cancel'))

    def testCancelMembershipPost(self):
        self.assertPost(reverse('cancel'), code=302, data=self.cancellation_data)
        membership = self.member.memberships.first()
        self.assertTrue(membership.canceled)
        # pay back the share
        if settings.ENABLE_SHARES:
            self.paid_share.refresh_from_db()
            self.paid_share.payback_date = self.paid_share.termination_date
            self.paid_share.save()
        # deactivate member
        self._testDeactivateMembership(membership)

    def testCancelMembershipPostWithUnpaidShares(self):
        self.assertPost(reverse('cancel'), code=302, member=self.member_with_unpaid_share,
                        data=self.cancellation_data)
        self.assertEqual(len(mail.outbox), 1)  # admin notification for membership
        self.assertTrue(self.cancellation_data['cancellation_comment'] in mail.outbox[0].body,
                        f'message not found in: {mail.outbox[0].body}')
        membership = self.member_with_unpaid_share.memberships.first()
        self.assertTrue(membership.canceled)
        self._testDeactivateMembership(membership)

    def testCancelMembershipWithCanceledShares(self):
        self.assertPost(reverse('cancel'), code=302, member=self.member_with_canceled_share,
                        data=self.cancellation_data)
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
        # don't cancel membership while keeping subscription
        response = self.assertPost(reverse('cancel'), code=200, member=self.member, data=self.cancellation_data | {
            f'primary_subscription_{sub.id}': 'keep',
            'shares': 0,
        })
        self.assertListEqual(
            ['membership'],
            list(response.context['form'].errors.keys())
        )
        self.member.refresh_from_db()
        self.assertFalse(self.member.canceled)
        self.assertFalse(self.member.memberships.first().canceled)
        self.assertEqual(len(mail.outbox), 0)
        # succeed when canceled
        sub.cancel()
        self.assertPost(reverse('cancel'), code=302, member=self.member, data=self.cancellation_data)
        self.assertTrue(self.member.memberships.first().canceled)
        # area admin gets notified, that member left the area and admin gets notified that member canceled membership
        self.assertEqual(len(mail.outbox), 2)

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


@override_settings(MEMBERSHIP={'cumulative_shares': True})
class MembershipWithCumulativeSharesTest(MembershipTests):
    pass


class MembershipAdminTests(JuntagricoTestCase):
    @classmethod
    def setUpTestData(cls):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        cls.default_member = Member.objects.get(email='admin@email.org')
        cls.member_requested = cls.create_member('member_requested@email.org', {'activation_date': None})
        cls.member_soon_active = cls.create_member('member_soon_active@email.org', {'activation_date': tomorrow})
        cls.member_active = cls.create_member('member_active@email.org', True)
        cls.member_canceled = cls.create_member('member_canceled@email.org', {'cancellation_date': '2026-03-13'})
        cls.member_soon_inactive = cls.create_member('member_soon_inactive@email.org', {
            'cancellation_date': '2026-03-13', 'deactivation_date': tomorrow,
        })
        cls.member_inactive = cls.create_member('member_inactive@email.org', {
            'cancellation_date': '2026-03-13', 'deactivation_date': '2026-03-13'
        })

    def testMembershipManageRequested(self):
        self.assertGet(reverse('manage-membership-requested'), 200)
        membership = self.member_requested.memberships.first()
        self.assertPost(reverse('manage-membership-activate'), {'membership_ids': membership.id}, 302)
        membership.refresh_from_db()
        self.assertTrue(membership.active)
        self.assertEqual(len(mail.outbox), 1)  # member notification

    def testMembershipManageActive(self):
        self.assertGet(reverse('manage-membership-active'), 200)
        membership = self.member_active.memberships.first()
        self.assertPost(reverse('manage-membership-cancel-deactivate'), {
            'membership_ids': membership.id,
            'cancellation_date': '2026-03-19',
        }, 302)
        membership.refresh_from_db()
        self.assertTrue(membership.canceled)
        self.assertEqual(len(mail.outbox), 0)  # no notification

    def testMembershipManageCancelAndDeactivate(self):
        membership = self.member_active.memberships.first()
        self.assertPost(reverse('manage-membership-cancel-deactivate'), {
            'membership_ids': membership.id,
            'cancellation_date': '2026-03-19',
            'deactivation_date': '2026-03-19'
        }, 302)
        membership.refresh_from_db()
        self.assertTrue(membership.inactive)
        self.assertEqual(len(mail.outbox), 1)  # member notification

    def testMembershipManageCancelAndDeactivateInvalid(self):
        # fails because cancellation date is missing
        membership = self.member_active.memberships.first()
        self.assertPost(reverse('manage-membership-cancel-deactivate'), {
            'membership_ids': membership.id,
            'deactivation_date': '2026-03-19'
        }, 302)
        membership.refresh_from_db()
        self.assertTrue(membership.active)
        self.assertEqual(len(mail.outbox), 0)  # no notification

    def testMembershipManageCanceled(self):
        self.assertGet(reverse('manage-membership-canceled'), 200)
        membership = self.member_canceled.memberships.first()
        self.assertPost(reverse('manage-membership-deactivate'), {'membership_ids': membership.id}, 302)
        membership.refresh_from_db()
        self.assertTrue(membership.inactive)
        self.assertEqual(len(mail.outbox), 1)  # member notification

    def testMembershipManageInactive(self):
        self.assertGet(reverse('manage-membership-archive'), 200)

    def testSecondMembership(self):
        membership = Membership.objects.create(account=self.member_inactive)
        membership.activate()
        Membership.objects.create(
            account=self.member_soon_active,
            activation_date='2026-02-13',
            cancellation_date='2026-02-15',
            deactivation_date='2026-02-20',
        )

    def testOverlappingMembershipFails(self):
        with self.assertRaises(ValidationError) as validation_error:
            Membership.objects.create(account=self.member_requested)
        self.assertEqual(validation_error.exception.code, 'overlap')
        with self.assertRaises(ValidationError) as validation_error:
            Membership.objects.create(account=self.member_active)
        self.assertEqual(validation_error.exception.code, 'overlap')
        with self.assertRaises(ValidationError) as validation_error:
            Membership.objects.create(account=self.member_soon_inactive)
        self.assertEqual(validation_error.exception.code, 'overlap')
        with self.assertRaises(ValidationError) as validation_error:
            Membership.objects.create(account=self.member_inactive, activation_date='2026-03-10')
        self.assertEqual(validation_error.exception.code, 'overlap')
        with self.assertRaises(ValidationError) as validation_error:
            Membership.objects.create(
                account=self.member_active,
                activation_date='2026-03-10',
                cancellation_date='2026-03-10',
                deactivation_date='2026-03-16',
            )
        self.assertEqual(validation_error.exception.code, 'overlap')


@tag('shares')
class MembershipSyncTests(MembershipTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.member_with_old_membership = cls.create_member(
            'member_with_old_membership@email.org', {
                'activation_date': '2026-03-01',
                'cancellation_date': '2026-03-19',
                'deactivation_date': '2026-03-19',
            }
        )
        cls.create_paid_share(cls.member_with_old_membership)

    @staticmethod
    def create_custom_share(member, paid_date='2017-03-27', **kwargs):
        data = {
            'member': member,
            'paid_date': paid_date,
            'issue_date': paid_date,
        }
        data.update(kwargs)
        return Share.objects.create(**data)

    def testMembershipSync(self):
        call_command('sync_memberships')
        # old memberships are not affected.
        self.assertFalse(self.member_with_old_membership.memberships.active_or_requested().exists())

    def testSyncWithoutMembership(self):
        member = self.member_without_membership
        self.assertEqual(member.memberships.count(), 0)
        sync(None, member)
        self.assertEqual(member.memberships.count(), 0)
        self.create_custom_share(member)
        sync(None, member)
        self.assertEqual(member.memberships.count(), 0)

    def testSyncActivatesRequestedMembership(self):
        member = self.create_member('sync_req@email.org', {'activation_date': None})
        membership = member.memberships.first()
        self.assertIsNone(membership.activation_date)
        self.create_custom_share(member, paid_date='2026-01-15')
        membership.refresh_from_db()
        self.assertEqual(membership.activation_date, datetime.date(2026, 1, 15))
        self.assertTrue(membership.active)

    def testSyncWithMultiplePaidSharesUsesEarliestPaidDate(self):
        member = self.create_member('sync_multi_shares@email.org', {'activation_date': None})
        membership = member.memberships.first()
        self.create_custom_share(member, paid_date='2026-02-10')
        self.create_custom_share(member, paid_date='2026-01-05')
        membership.refresh_from_db()
        self.assertEqual(membership.activation_date, datetime.date(2026, 1, 5))

    def testSyncActivationDateAdjustedForPreviousMembership(self):
        member = self.create_member(
            'sync_prev_membership@email.org',
            {
                'activation_date': '2026-02-01',
                'cancellation_date': '2026-02-15',
                'deactivation_date': '2026-02-15',
            }
        )
        new_membership = Membership.objects.create(account=member, activation_date=None)
        self.create_custom_share(member, paid_date='2026-01-01')
        new_membership.refresh_from_db()
        self.assertEqual(new_membership.activation_date, datetime.date(2026, 2, 16))

        new_membership.activation_date = None
        new_membership.save()
        member.share_set.all().delete()
        self.create_custom_share(member, paid_date='2026-03-01')
        new_membership.refresh_from_db()
        self.assertEqual(new_membership.activation_date, datetime.date(2026, 3, 1))

    def testSyncDeactivatesMembershipWhenSharesInsufficient(self):
        member = self.create_member('sync_deactivate@email.org', True)
        membership = member.memberships.first()
        self.assertTrue(membership.active)
        self.create_custom_share(
            member,
            paid_date='2026-01-01',
            cancelled_date='2026-03-01',
            termination_date='2026-03-01',
            payback_date='2026-03-15',
        )
        membership.refresh_from_db()
        self.assertEqual(membership.cancellation_date, datetime.date(2026, 3, 1))
        self.assertEqual(membership.deactivation_date, datetime.date(2026, 3, 15))

    def testSyncPreservesExistingCancellationDateWhenDeactivating(self):
        member = self.create_member(
            'sync_preserve_cancel@email.org',
            {'activation_date': '2026-01-01', 'cancellation_date': '2026-02-10'}
        )
        membership = member.memberships.first()
        self.create_custom_share(
            member,
            paid_date='2026-01-01',
            cancelled_date='2026-03-01',
            termination_date='2026-03-01',
            payback_date='2026-03-15',
        )
        membership.refresh_from_db()
        self.assertEqual(membership.cancellation_date, datetime.date(2026, 2, 10))
        self.assertEqual(membership.deactivation_date, datetime.date(2026, 3, 15))

    def testSyncClearsDuplicateMemberships(self):
        member = self.create_member('sync_duplicates@email.org')
        Membership.objects.bulk_create([
            Membership(account=member),
            Membership(account=member),
        ])
        self.assertEqual(member.memberships.active_or_requested().count(), 2)
        sync(None, member)
        self.assertEqual(member.memberships.active_or_requested().count(), 1)

    def testSyncPreservesMembershipIfNotAllSharesCancelled(self):
        member = self.create_member('sync_signals@email.org', {'activation_date': None})
        self.create_custom_share(member, paid_date='2026-01-10')
        membership = member.memberships.first()
        self.assertEqual(membership.activation_date, datetime.date(2026, 1, 10))
        self.assertTrue(membership.active)

        # 2. Add a canceled/paid-back share for the member
        self.create_custom_share(
            member,
            paid_date='2026-01-01',
            cancelled_date='2026-03-01',
            termination_date='2026-03-01',
            payback_date='2026-03-15',
        )
        # Membership is still active because active_share exists
        membership.refresh_from_db()
        self.assertIsNone(membership.deactivation_date)

    def testSyncDisabledSettings(self):
        member = self.create_member('sync_disabled@email.org', {'activation_date': None})
        membership = member.memberships.first()
        self.create_custom_share(member, paid_date='2026-01-10')
        membership.activation_date = None
        membership.save()

        with override_settings(ENABLE_SHARES=False):
            sync(None, member)
            membership.refresh_from_db()
            self.assertIsNone(membership.activation_date)

        with override_settings(MEMBERSHIP={'enable': False}):
            sync(None, member)
            membership.refresh_from_db()
            self.assertIsNone(membership.activation_date)

        with override_settings(MEMBERSHIP={'sync_shares': False}):
            sync(None, member)
            membership.refresh_from_db()
            self.assertIsNone(membership.activation_date)

        with override_settings(MEMBERSHIP={'required_shares': 0}):
            sync(None, member)
            membership.refresh_from_db()
            self.assertIsNone(membership.activation_date)

    @override_settings(MEMBERSHIP={'enable': True, 'required_shares': 1, 'cumulative_shares': True, 'sync_shares': True})
    def testSyncCumulativeShares(self):
        member = self.create_member('sync_cumul@email.org', {'activation_date': None})
        membership = member.memberships.first()
        self.set_up_depots()
        self.set_up_sub_types()
        sub = self.create_sub_now(self.depot)
        member.join_subscription(sub, True)
        self.assertEqual(member.required_shares_count, 1)

        # first share is needed for subscription
        self.create_custom_share(member, paid_date='2026-01-10')
        membership.refresh_from_db()
        self.assertIsNone(membership.activation_date)

        # second share is available for membership
        self.create_custom_share(member, paid_date='2026-01-20')
        membership.refresh_from_db()
        self.assertEqual(membership.activation_date, datetime.date(2026, 1, 10))

    @override_settings(MEMBERSHIP={'enable': True, 'required_shares': 2, 'cumulative_shares': False, 'sync_shares': True})
    def testSyncMultipleRequiredShares(self):
        member = self.create_member('sync_multi_req@email.org', {'activation_date': None})
        membership = member.memberships.first()

        # first share doesn't activate membership
        self.create_custom_share(member, paid_date='2026-01-10')
        membership.refresh_from_db()
        self.assertIsNone(membership.activation_date)

        # second share activates membership
        self.create_custom_share(member, paid_date='2026-01-20')
        membership.refresh_from_db()
        self.assertEqual(membership.activation_date, datetime.date(2026, 1, 10))
