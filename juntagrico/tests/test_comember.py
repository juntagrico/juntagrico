import datetime

from django.conf import settings
from django.core import mail
from django.urls import reverse

from juntagrico.models import Member, Share, Subscription, SubscriptionMembership
from . import JuntagricoTestCase


class CoMemberTests(JuntagricoTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.co_member = cls.create_member('co_member@email.org', iban='CH6189144414396247884')
        # add member, that just left another subscription
        cls.switching_co_member = cls.create_member('co_member2@email.org', iban='CH6189144414396247884')
        cls.old_sub = cls.create_sub(cls.depot, [cls.sub_type], datetime.date(2025, 1, 27))
        SubscriptionMembership.objects.create(
            member=cls.switching_co_member,
            subscription=cls.old_sub,
            join_date=cls.old_sub.activation_date,
            leave_date=datetime.date.today(),
        )
        mail.outbox.clear()

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
        if settings.ENABLE_SHARES:
            self.assertEqual(Share.objects.filter(member__email=new_co_member_data['email']).count(), 1)
        self.assertEqual(Subscription.objects.filter(subscriptionmembership__member__email=new_co_member_data['email']).count(), 1)
        # membership and, if enabled, share order emails to co-member & admin notifications for the same
        self.assertEqual(len(mail.outbox), 4 if settings.ENABLE_SHARES else 2)

    def testAddExistingCoMemberWithSub(self):
        # existing member with subs can not be added as co members
        # message to contact admin will show
        new_co_member_data = self.get_co_member_data(self.member2.email)
        # response is 200 (form error)
        response = self.assertPost(reverse('add-member', args=[self.sub.pk]), new_co_member_data)
        self.assertListEqual(
            ['has_active_subscription'],  # first code 'part_activation_date_mismatch' reaches here as none somehow
            [e.code for e in response.context_data['form'].errors['email'].as_data()]
        )
        # no new shares should be created
        self.assertEqual(Share.objects.filter(member=self.member2).count(), 0)
        # member now is not part of subscription
        self.assertNotEqual(self.member2.subscription_current, self.sub)

    def testAddExistingCoMemberWithSubEndingSameDay(self):
        # corner case: co-member just left their other subscription today. New subscription will be joined tomorrow
        new_co_member_data = self.get_co_member_data(self.switching_co_member.email)
        self.assertPost(reverse('add-member', args=[self.sub.pk]), new_co_member_data, 302)
        self.switching_co_member.refresh_from_db()
        self.assertIsNone(self.co_member.subscription_current)
        self.assertTrue(
            self.switching_co_member.subscriptionmembership_set.filter(
                subscription=self.sub,
                join_date=datetime.date.today() + datetime.timedelta(days=1)
            ).exists()
        )

    def testAddExistingCoMember(self):
        co_member_before = self.co_member.__dict__
        new_co_member_data = self.get_co_member_data(self.co_member.email)
        self.assertPost(reverse('add-member', args=[self.sub.pk]), new_co_member_data, 302)
        self.co_member.refresh_from_db()
        # member still exists and is unchanged
        self.assertEqual(self.co_member.id, co_member_before['id'])
        self.assertEqual(self.co_member.user_id, co_member_before['user_id'])
        self.assertEqual(self.co_member.iban, co_member_before['iban'])
        self.assertEqual(self.co_member.addr_street, co_member_before['addr_street'])
        self.assertEqual(self.co_member.first_name, co_member_before['first_name'])
        # no new shares should be created
        self.assertEqual(Share.objects.filter(member=self.co_member).count(), 0)
        # member now is part of subscription
        self.assertEqual(self.co_member.subscription_current, self.sub)
