import datetime

from django.template import Template, Context
from django.urls import reverse

from . import JuntagricoTestCase
from ..entity.share import Share
from ..entity.subs import SubscriptionPart


class ShareTests(JuntagricoTestCase):
    fixtures = JuntagricoTestCase.fixtures + ['test/shares']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.load_shares()

    @classmethod
    def load_shares(cls):
        cls.share1, cls.share2, cls.share3 = Share.objects.order_by('id')[:3]

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
        cancelled_share = Share.objects.create(member=self.member2, cancelled_date=yesterday)
        future_terminated_share = Share.objects.create(
            member=self.member3, cancelled_date=yesterday, termination_date=tomorrow
        )
        terminated_share = Share.objects.create(
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
            unpaid_share, cancelled_share, future_terminated_share, unneeded_unpaid_share
        ])
        # member2 has no access
        self.assertGet(reverse('manage-share-unpaid'), member=self.member2, code=302)
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
            msg="\nfirst should be yes, because unpaid share of member 3 is cancelled"
                "\nsecond is a plain yes for member 2"
                "\nthird could also be paid by member 1"
                "\nlast is a not required share of member 4"
        )

    def testShareAdmin(self):
        url = reverse('admin:juntagrico_share_changelist')
        selected_items = [self.member.share_set.first().pk]
        self.assertPost(url, data={'action': 'mass_edit_share_dates', '_selected_action': selected_items},
                        member=self.admin)

    def testShareCertificate(self):
        self.client.force_login(self.member.user)
        response = self.client.get(reverse('share-certificate') + '?year=2017')
        self.assertEqual(response['content-type'], 'application/pdf')

    def testMemberShareCancel(self):
        share = self.member.share_set.first()
        self.assertGet(reverse('share-cancel', args=[share.pk]), 302)
        # TODO: Test cancellation date

    def testManageShareCanceledList(self):
        self.assertGet(reverse('manage-share-cancelled'))
        self.assertGet(reverse('manage-share-cancelled'), member=self.member2, code=302)

    def testManageSharePayout(self):
        share = self.member.share_set.first()
        share.cancelled_date = datetime.date.today()
        share.termination_date = datetime.date.today()
        share.save()
        self.assertGet(reverse('manage-share-payout-single', args=[share.pk]), 302)
        self.assertEqual(self.member2.active_shares.count(), 0)
        # TODO: test manage-share-payout
