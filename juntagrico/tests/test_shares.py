import datetime

from django.core.exceptions import ValidationError
from django.template import Template, Context
from django.core import mail
from django.test import tag, override_settings
from django.urls import reverse

from . import JuntagricoTestCase
from ..entity.member import SubscriptionMembership
from ..entity.membership import Membership
from ..entity.share import Share
from ..entity.subs import SubscriptionPart


@tag('shares')
class ShareTestCase(JuntagricoTestCase):
    fixtures = JuntagricoTestCase.fixtures + ['test/shares']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.load_shares()

    @classmethod
    def load_shares(cls):
        cls.share1, cls.share2, cls.share3 = Share.objects.order_by('id')[:3]


class ShareTests(ShareTestCase):
    def testMemberShareManage(self):
        self.assertGet(reverse('manage-shares'), 200)
        self.assertGet(reverse('manage-shares'), 200, member=self.member4)
        self.assertPost(reverse('manage-shares'), {'shares': 0}, 200, member=self.member2)
        self.member2.refresh_from_db()
        self.assertEqual(self.member2.share_set.count(), 0)
        self.assertPost(reverse('manage-shares'), {'shares': 1}, 302, member=self.member2)
        self.member2.refresh_from_db()
        self.assertEqual(self.member2.share_set.count(), 1)

    def testAdminCreateShare(self):
        url = reverse('admin:juntagrico_share_add')
        self.assertPost(url, data={'member': self.member.id, 'value': "250.0"},
                        member=self.admin, code=302)
        self.assertEqual(self.member.share_set.count(), 2)

    def testManageShareUnpaidList(self):
        # setup
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        unpaid_share = Share.objects.create(member=self.member)
        canceled_share = Share.objects.create(member=self.member2, cancelled_date=yesterday)
        future_terminated_share = Share.objects.create(
            member=self.member3, cancelled_date=yesterday, termination_date=tomorrow
        )
        # terminated share (should not show)
        Share.objects.create(
            member=self.member4, cancelled_date=yesterday, termination_date=yesterday
        )
        unneeded_unpaid_share = Share.objects.create(member=self.member4)
        # additional part that needs shares for member 1 and 3
        SubscriptionPart.objects.create(subscription=self.sub, type=self.sub_type)
        # additional part that needs shares for member 2
        SubscriptionPart.objects.create(subscription=self.sub2, type=self.sub_type)

        # test
        response = self.assertGet(reverse('manage-share-unpaid'))
        # make sure the right shares are shown
        self.assertEqual(list(response.context['object_list'].order_by('id')), [
            unpaid_share, canceled_share, future_terminated_share, unneeded_unpaid_share
        ])
        # member2 has no access
        self.assertGet(reverse('manage-share-unpaid'), member=self.member2, code=403)
        # Test share count templatetag
        rendered = Template(
            '{% load juntagrico.share %}'
            '{% regroup management_list by member as shares_list %}'
            '{% for member, shares in shares_list %}'
            '{% for share in shares %}'
            '{% required_for_subscription share forloop.counter %},'
            '{% endfor %}'
            '{% endfor %}'
        ).render(Context({'management_list': response.context['object_list']}))
        self.assertEqual(
            rendered,
            'Ja,Ja,Ja. Oder first_name1 last_name1. (1 insgesamt),Nein,',
            msg="\nfirst should be yes, because unpaid share of member 3 is canceled"
                "\nsecond is a plain yes for member 2"
                "\nthird could also be paid by member 1"
                "\nlast is a not required share of member 4"
        )

    def testShareAdmin(self):
        url = reverse('admin:juntagrico_share_changelist')
        selected_items = [self.member.share_set.first().pk]
        self.assertPost(url, data={'action': 'mass_edit_share_dates', '_selected_action': selected_items},
                        member=self.admin)

    def testIncompleteShareAddFails(self):
        url = reverse('admin:juntagrico_share_add')
        response = self.assertPost(url, data={'member': ''}, member=self.admin)
        self.assertListEqual(
            [ValidationError],
            [type(e) for e in response.context_data['errors'].as_data()]
        )

    def testShareCertificate(self):
        self.client.force_login(self.member.user)
        response = self.client.get(reverse('share-certificate') + '?year=2017')
        self.assertEqual(response['content-type'], 'application/pdf')

    def testMemberCantCancelShare(self):
        # member can not cancel share because it is used
        share = self.member.share_set.last()
        self.assertGet(reverse('share-cancel', args=[share.pk]), 302)
        share.refresh_from_db()
        self.assertIsNone(share.cancelled_date)


class ShareCancelTests(ShareTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # add share to cancel
        cls.spare_share = cls.create_paid_share(cls.member)
        mail.outbox.clear()

    def testMemberShareCancel(self):
        self.assertGet(reverse('share-cancel', args=[self.spare_share.pk]), 302)
        self.spare_share.refresh_from_db()
        self.assertEqual(self.spare_share.cancelled_date, datetime.date.today())
        self.assertIsNotNone(self.spare_share.termination_date)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['email1@email.org'])

    def testCancelWrongShareFails(self):
        share = self.member4.share_set.first()
        self.assertGet(reverse('share-cancel', args=[share.pk]), 404)
        share.refresh_from_db()
        self.assertEqual(share.cancelled_date, None)
        self.assertEqual(share.termination_date, None)

    def testUnifiedCancellation(self):
        self.assertGet(reverse('cancel'), 200)
        before = self.member.usable_shares.count()
        data = {
            'activity_areas': [self.area.id],
            'shares': 1,
            'iban': 'CH61 0900 0000 1900 0012 6',
            'addr_street': 'addr_street',
            'addr_zipcode': ' 1234',
            'addr_location': 'addr_location',
            f'primary_subscription_{self.sub.pk}': 'keep',
            'membership': True,
            'account': True,
        }
        self.assertPost(reverse('cancel'), data=data, code=302)
        self.member.refresh_from_db()
        self.assertEqual(before - 1, self.member.usable_shares.count())
        self.assertEqual(len(mail.outbox), 1)  # admin notification

    def testCancelRequiredSharesFails(self):
        self.assertGet(reverse('cancel'), 200)
        if self.member.memberships.active_or_requested().first() is None:
            Membership.objects.create(account=self.member)
        before = self.member.usable_shares.count()
        data = {
            'activity_areas': [self.area.id],
            'shares': 2,
            'iban': 'CH61 0900 0000 1900 0012 6',
            'addr_street': 'addr_street',
            'addr_zipcode': ' 1234',
            'addr_location': 'addr_location',
            f'primary_subscription_{self.sub.pk}': 'keep',
            'membership': True,
            'account': True,
        }
        response = self.assertPost(reverse('cancel'), data=data, code=200)
        self.assertListEqual(
            ['shares'],
            list(response.context['form'].errors.keys())
        )
        self.member.refresh_from_db()
        self.assertEqual(before, self.member.usable_shares.count())


@override_settings(MEMBERSHIP={'cumulative_shares': True})
class CumulativeShareTests(ShareTests):
    pass


@override_settings(MEMBERSHIP={'cumulative_shares': True, 'sync_shares': False})
class CumulativeShareCancelTests(ShareCancelTests):
    pass


class ShareCountTests(ShareTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Share.objects.create(member=cls.member)
        Share.objects.create(member=cls.member2)
        Share.objects.create(member=cls.member3)
        Share.objects.create(member=cls.member4)
        for _ in range(3):
            Share.objects.create(member=cls.member5)
        SubscriptionMembership.objects.create(
            member=cls.member5, subscription=cls.sub
        )
        cls.sub_type3.shares = 3
        cls.sub_type3.save()
        cls.create_membership(cls.member)
        cls.create_membership(cls.member2)
        cls.member3.memberships.all().delete()
        cls.create_membership(cls.member4)
        # sub with negative share requirement
        cls.sub_type_with_negative_shares = cls.create_sub_type(cls.bundle, shares=-3)
        cls.sub_with_negative_shares = cls.create_sub_now(
            cls.depot, [cls.sub_type_with_negative_shares, cls.sub_type]
        )
        cls.member8 = cls.create_member('member8@example.com')
        cls.member8.join_subscription(cls.sub_with_negative_shares, True)

    def testMemberRequiredSharesForSubscription(self):
        # in shared active sub
        self.assertEqual(self.member.required_shares_count, 0)
        # in waiting sub
        self.assertEqual(self.member2.required_shares_count, 2)
        # in inactive sub and new shared sub
        self.assertEqual(self.member3.required_shares_count, 0)
        # without sub
        self.assertEqual(self.member4.required_shares_count, 0)
        # not yet joined future sub
        self.assertEqual(self.member5.required_shares_count, 0)
        # including parts with negative required shares -> required_shares_count is always >= 0
        self.assertEqual(self.member8.required_shares_count, 0)

    def testSubscriptionRequiredShares(self):
        self.assertEqual(self.sub.required_shares, 1)
        self.assertEqual(self.sub2.required_shares, 2)
        # inactive parts don't required shares
        self.assertEqual(self.sub3.required_shares, 0)
        # subscription requiring negative subs
        self.assertEqual(self.sub_with_negative_shares.required_shares, -2)

    def testSubscriptionShareOverflow(self):
        self.assertEqual(self.sub.share_overflow, 2)
        self.assertEqual(self.sub2.share_overflow, -1)
        self.assertEqual(self.sub3.share_overflow, 1)


@override_settings(MEMBERSHIP={'cumulative_shares': True})
class CumulativeShareCountTests(ShareCountTests):
    def testSubscriptionShareOverflow(self):
        self.assertEqual(self.sub.share_overflow, 1)
        self.assertEqual(self.sub2.share_overflow, -2)
        self.assertEqual(self.sub3.share_overflow, 1)


class ShareManageTests(ShareTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # add all states of shares
        Share.objects.create(member=cls.member2)
        Share.objects.create(member=cls.member2, cancelled_date='2025-08-10', termination_date='2025-12-31')
        cls.create_paid_share(cls.member2, cancelled_date='2025-08-10', termination_date='2025-12-31')
        cls.create_paid_share(
            cls.member2, cancelled_date='2025-08-10', termination_date='2025-12-31', payback_date='2025-12-31'
        )
        mail.outbox.clear()
    
    def testManageShares(self):
        self.assertGet(reverse('manage-share'), 200)
        self.assertGet(reverse('manage-share'), 200, member=self.admin)
        self.assertGet(reverse('manage-share'), 403, member=self.member2)

    def testCancelShareForMember(self):
        # member2 can't cancel shares
        self.assertPost(
            reverse('manage-share-cancel'), {'share_id': self.share1.id}, 302, self.member2
        )
        self.assertEqual(len(mail.outbox), 0)  # no member notification
        self.share1.refresh_from_db()
        self.assertIsNone(self.share1.cancelled_date)
        # member1 can cancel shares
        self.assertPost(
            reverse('manage-share-cancel'), {'share_id': f'{self.share1.id}_{self.share2.id}'}, 302
        )
        self.assertEqual(len(mail.outbox), 2)  # member notifications
        self.share1.refresh_from_db()
        self.assertIsNotNone(self.share1.cancelled_date)
        self.share2.refresh_from_db()
        self.assertIsNotNone(self.share2.cancelled_date)

    def testCancelCanceledShareFails(self):
        original_cancellation_date = self.share3.cancelled_date
        self.assertPost(
            reverse('manage-share-cancel'), {'share_id': self.share3.id}, 302
        )
        self.assertEqual(len(mail.outbox), 0)  # no member notification
        self.share3.refresh_from_db()
        self.assertEqual(self.share3.cancelled_date, original_cancellation_date)

    def testCancelShareForMemberWithChangeDate(self):
        today = datetime.date.today()
        self.assertPost(reverse('changedate-set'), data={'date': '1999-01-01'}, code=302)
        self.assertPost(
            reverse('manage-share-cancel'), {'share_id': self.share2.id}, 302
        )
        self.share2.refresh_from_db()
        self.assertEqual(today, self.share2.cancelled_date)

    def testManageShareCanceledList(self):
        # create share with future termination date for test
        today = datetime.date.today()
        Share.objects.create(
            member=self.member,
            paid_date=today,
            issue_date=today,
            cancelled_date=today,
            termination_date=today + datetime.timedelta(days=10),
        )
        self.assertGet(reverse('manage-share-canceled'))
        self.assertGet(reverse('manage-share-canceled'), member=self.member2, code=403)

    def testManageSharePayoutSingle(self):
        membership = (
            self.member.memberships.active_or_requested().first()
            or Membership.objects.create(
                account=self.member,
                activation_date='2026-03-13',
                cancellation_date='2026-03-13',
            )
        )
        share = self.member.share_set.first()
        share.cancelled_date = datetime.date.today()
        share.termination_date = datetime.date.today()
        share.save()
        self.assertGet(reverse('manage-share-payout-single', args=[share.pk]), 302)
        self.assertEqual(self.member.active_shares.count(), 0)
        membership.refresh_from_db()
        self.assertTrue(membership.inactive)

    def testManageSharePayout(self):
        shares = Share.objects.filter(payback_date=None)
        today = datetime.date.today()
        for share in shares:
            share.cancelled_date = today
            share.termination_date = today
            share.save()
        self.assertPost(
            reverse('manage-share-payout'),
            {'share_ids': '_'.join(map(str, shares.values_list('pk', flat=True)))},
            302
        )
        self.assertEqual(self.member.active_shares.count(), 0)
        self.assertEqual(self.member4.active_shares.count(), 0)
        self.assertEqual(self.member5.active_shares.count(), 0)

    def testManageArchivedShares(self):
        self.assertGet(reverse('manage-share-archive'), 200)
        self.assertGet(reverse('manage-share-archive'), 200, member=self.admin)
        self.assertGet(reverse('manage-share-archive'), 403, member=self.member2)

    def testManageSharesByAccount(self):
        self.assertGet(reverse('manage-share-by-account', args=[self.member.id]), 200)
        self.assertGet(reverse('manage-share-by-account', args=[self.member.id]), 200, member=self.admin)
        self.assertGet(reverse('manage-share-by-account', args=[self.member.id]), 403, member=self.member2)
        self.assertGet(reverse('manage-share-by-account', args=[self.member2.id]), 200)
        self.assertGet(reverse('manage-share-by-account', args=[self.member3.id]), 200)
        self.assertGet(reverse('manage-share-by-account', args=[self.inactive_member.id]), 200)

    @override_settings(MEMBERSHIP={'cumulative_shares': True})
    def testManageSharesByAccountWithCumulativeShares(self):
        self.testManageSharesByAccount()

    @override_settings(MEMBERSHIP={'enable': False})
    def testManageSharesByAccountWithoutMemberships(self):
        self.testManageSharesByAccount()
