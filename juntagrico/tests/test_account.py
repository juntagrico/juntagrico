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
            'comment': 'a personal message',
        }
        self.assertPost(reverse('cancel'), code=302, member=self.member_without_shares, data=data)
        self.assertEqual(len(mail.outbox), 1)  # admin notification
        self.assertTrue(data['comment'] in mail.outbox[0].body, f'message not found in: {mail.outbox[0].body}')
        self.member_without_shares.refresh_from_db()
        self.assertTrue(self.member_without_shares.canceled)
        self._testDeactivateAccount(self.member_without_shares)

    def _testDeactivateAccount(self, account):
        self.assertPost(
            reverse('manage-member-deactivate'),
            {'member_ids': str(account.pk)},
            member=self.admin,
            code=302
        )
        account.refresh_from_db()
        self.assertTrue(account.inactive, f'{account} {account.email}')
