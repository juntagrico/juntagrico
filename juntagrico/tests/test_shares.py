import datetime

from django.core.exceptions import ValidationError
from django.template import Template, Context
from django.core import mail
from django.test import tag
from django.urls import reverse

from . import JuntagricoTestCase
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

    def testManageShareCanceledList(self):
        self.assertGet(reverse('manage-share-canceled'))
        self.assertGet(reverse('manage-share-canceled'), member=self.member2, code=403)

    def testManageSharePayoutSingle(self):
        share = self.member.share_set.first()
        share.cancelled_date = datetime.date.today()
        share.termination_date = datetime.date.today()
        share.save()
        self.assertGet(reverse('manage-share-payout-single', args=[share.pk]), 302)
        self.assertEqual(self.member.active_shares.count(), 0)

    def testManageSharePayout(self):
        shares = Share.objects.all()
        for share in shares:
            share.cancelled_date = datetime.date.today()
            share.termination_date = datetime.date.today()
            share.save()
        self.assertPost(
            reverse('manage-share-payout'),
            {'share_ids': '_'.join(map(str, shares.values_list('pk', flat=True)))},
            302
        )
        self.assertEqual(self.member.active_shares.count(), 0)
        self.assertEqual(self.member4.active_shares.count(), 0)
        self.assertEqual(self.member5.active_shares.count(), 0)


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
