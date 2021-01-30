from django.urls import reverse

from juntagrico.models import Member, Share, Subscription
from test.util.test import JuntagricoTestCase


class CoMemberTests(JuntagricoTestCase):

    def setUp(self):
        super().setUp()
        self.member5 = self.create_member('email5@email.org')
        self.member5.iban = 'CH6189144414396247884'
        self.member5.save()

    @staticmethod
    def get_co_member_data(email):
        return {
            'first_name': 'co_member_first_name',
            'last_name': 'co_member_last_name',
            'email': email,
            'addr_street': 'co_member_addr_street',
            'addr_zipcode': '1000',  # must be <= 10 chars
            'addr_location': 'co_member_addr_location',
            'phone': 'co_member_phone',
            'shares': 1
        }

    def testAccess(self):
        # main member of sub has access
        self.assertGet(reverse('add-member', args=[self.sub.pk]))
        # other members of sub do not have access
        self.assertGet(reverse('add-member', args=[self.sub.pk]), 302, self.member3)

    def testAddNewCoMember(self):
        new_co_member_data = self.get_co_member_data('new_comember@juntagrico.org')
        self.assertPost(reverse('add-member', args=[self.sub.pk]), new_co_member_data, 302)
        self.assertEqual(Member.objects.filter(email=new_co_member_data['email']).count(), 1)
        self.assertEqual(Share.objects.filter(member__email=new_co_member_data['email']).count(), 1)
        self.assertEqual(Subscription.objects.filter(subscriptionmembership__member__email=new_co_member_data['email']).count(), 1)

    def testAddExistingCoMemberWithSub(self):
        # existing member with subs can not be added as co members
        # message to contact admin will show
        new_co_member_data = self.get_co_member_data(self.member2.email)
        # response is 200 (form error)
        self.assertPost(reverse('add-member', args=[self.sub.pk]), new_co_member_data)
        # no new shares should be created
        self.assertEqual(Share.objects.filter(member=self.member2).count(), 0)
        # member now is not part of subscription
        self.assertNotEqual(self.member2.subscription_current, self.sub)

    def testAddExistingCoMember(self):
        co_member_before = self.member5.__dict__
        new_co_member_data = self.get_co_member_data(self.member5.email)
        self.assertPost(reverse('add-member', args=[self.sub.pk]), new_co_member_data, 302)
        self.member5.refresh_from_db()
        # member still exists and is unchanged
        self.assertEqual(self.member5.id, co_member_before['id'])
        self.assertEqual(self.member5.user_id, co_member_before['user_id'])
        self.assertEqual(self.member5.iban, co_member_before['iban'])
        self.assertEqual(self.member5.addr_street, co_member_before['addr_street'])
        self.assertEqual(self.member5.first_name, co_member_before['first_name'])
        # no new shares should be created
        self.assertEqual(Share.objects.filter(member=self.member5).count(), 0)
        # member now is part of subscription
        self.assertEqual(self.member5.subscription_current, self.sub)
