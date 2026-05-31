from django.conf import settings
from django.contrib.auth.models import Permission
from django.core import mail
from django.urls import reverse

from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from . import JuntagricoTestCase


class AccountTests(JuntagricoTestCase):

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
            Permission.objects.get(codename='notified_on_member_cancellation'),
        )

    def testCancelAccountPost(self):
        data = {
            'account': False,
            'cancellation_comment': 'a personal message',
        }
        self.assertPost(reverse('cancel'), code=302, member=self.member_without_shares, data=data)
        self.assertEqual(len(mail.outbox), 1)  # admin notification
        self.assertTrue(data['cancellation_comment'] in mail.outbox[0].body, f'message not found in: {mail.outbox[0].body}')
        self.member_without_shares.refresh_from_db()
        self.assertTrue(self.member_without_shares.canceled)
        self._testDeactivateAccount(self.member_without_shares)

    def testCancelAccountFails(self):
        # can't cancel account until other entities are canceled
        response = self.assertPost(reverse('cancel'), code=200, data={
            'membership': True,
            'shares': 0,
            'account': False,
        })
        self.assertListEqual(
            ['account'],
            list(response.context['form'].errors.keys())
        )
        self.member.refresh_from_db()
        self.assertFalse(self.member.canceled)

    def _testDeactivateAccount(self, account):
        self.assertPost(
            reverse('manage-member-deactivate'),
            {'member_ids': str(account.pk)},
            member=self.admin,
            code=302
        )
        account.refresh_from_db()
        self.assertTrue(account.inactive, f'{account} {account.email}')


class AdminTest(JuntagricoTestCase):
    def testDeleteComments(self):
        member = self.member
        member.signup_comment = 'signup comment'
        member.cancellation_comment = 'cancellation comment'
        member.save()
        self.assertGet(reverse('admin:juntagrico_member_change', args=[member.id]), member=self.admin)
        data = {
            'addr_location': 'addr_location',
            'addr_street': 'addr_street',
            'addr_zipcode': '1234',
            'email': 'email1@email.org',
            'first_name': 'first_name1',
            'last_name': 'last_name1',
            'mobile_phone': 'phone',
            'phone': 'phone',
            'memberships-TOTAL_FORMS': '0',
            'memberships-INITIAL_FORMS': '0',
            'subscriptionmembership_set-TOTAL_FORMS': '0',
            'subscriptionmembership_set-INITIAL_FORMS': '0',
            'delete_signup_comment': 'on',
            'delete_cancellation_comment': 'on',
            '_save': 'save'
        }
        self.assertPost(reverse('admin:juntagrico_member_change', args=[member.id]),
                        data=data, member=self.admin, code=302)
        member.refresh_from_db()
        self.assertEqual(member.signup_comment, '')
        self.assertEqual(member.cancellation_comment, '')
