import datetime
import uuid

from django.conf import settings
from django.core import mail
from django.test import override_settings, tag
from django.urls import reverse

from juntagrico.models import Share, SubscriptionMembership
from . import JuntagricoTestCase
from .test_cs import CreateSubscriptionTestCase
from ..entity.member import Invitee
from ..entity.membership import Membership


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
        self.assertEqual(Invitee.objects.filter(email=new_co_member_data['email']).count(), 1)
        if settings.ENABLE_SHARES:
            # share is not created yet
            self.assertEqual(Share.objects.filter(member__email=new_co_member_data['email']).count(), 0)
        # invitation email
        self.assertEqual(len(mail.outbox), 1)

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
        # invitation created
        self.assertTrue(Invitee.objects.filter(email=co_member_before['email']).exists())


class InvitationTests(CreateSubscriptionTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.invitee = Invitee.objects.create(
            email='invitee@juntagrico.invalid',
            first_name='Invitee',
            last_name='Juntagrico',
            subscription=cls.sub,
            invited_by=cls.sub.primary_member,
        )
        if settings.ENABLE_SHARES:
            cls.invitee.shares = 2
            cls.invitee.save()
        cls.existing_invitee = Invitee.objects.create(
            email=cls.member2.email,
            first_name='Invitee',
            last_name='Juntagrico',
            subscription=cls.sub,
            invited_by=cls.sub.primary_member,
        )
        cls.expired_invitation = Invitee.objects.create(
            email='expired@juntagrico.invalid',
            first_name='Invitee',
            last_name='Juntagrico',
            subscription=cls.sub,
            invited_by=cls.member4,
        )

    def assertHasMembership(self, email='new_member@juntagrico.invalid'):
        self.assertTrue(
            Membership.objects.filter(
                account__email=email
            ).exists()
        )

    def testInvalidInvitation(self):
        invalid_key = uuid.uuid4()
        self.assertGet(reverse('invitation', args=[invalid_key]), 200)
        self.assertGet(reverse('invitation-new', args=[invalid_key]), 200)
        self.client.force_login(self.member2.user)
        self.assertGet(reverse('invitation-existing', args=[invalid_key]), 200)

    def testInvitationBanner(self):
        self.client.force_login(self.member2.user)
        response = self.assertGet(reverse('home'), 200, self.member2)
        self.assertContains(
            response,
            f'<a class="btn btn-info" href="{reverse("invitation-existing", args=[self.existing_invitee.key])}">',
        )

    def testInvitationInvalidation(self):
        # if inviter is not in subscription (anymore) invitation becomes invalid
        self.assertGet(reverse('invitation', args=[self.expired_invitation.key]), 200)
        with self.assertRaises(Invitee.DoesNotExist):
            self.expired_invitation.refresh_from_db()

    def testAcceptInvitationNew(self):
        self.assertGet(reverse('invitation', args=[self.invitee.key]), 200)
        self.assertGet(reverse('invitation-new', args=[self.invitee.key]), 200)

        data = self.newMemberData('new_member@juntagrico.invalid')
        if settings.ENABLE_SHARES:
            data.update({'of_member': 1})
        self.assertPost(
            reverse('invitation-new', args=[self.invitee.key]),
            data,
            302,
        )
        self.assertTrue(self.sub.current_members.filter(email='new_member@juntagrico.invalid').exists())

    @tag('shares')
    def testAcceptInvitationWithoutShares(self):
        data = self.newMemberData('new_member@juntagrico.invalid')
        # fails if shares is needed
        data.update({'of_member': 0})
        self.assertPost(
            reverse('invitation-new', args=[self.invitee.key]),
            data,
            200,
        )
        self.assertFalse(
            self.sub.current_members.filter(
                email='new_member@juntagrico.invalid'
            ).exists()
        )
        # if member has enough shares, invitation can be accepted without shares
        self.create_paid_share(self.member)
        self.assertPost(
            reverse('invitation-new', args=[self.invitee.key]),
            data,
            302,
        )
        self.assertTrue(
            self.sub.current_members.filter(
                email='new_member@juntagrico.invalid'
            ).exists()
        )

    @tag('shares')
    def testAcceptInvitationNewWithMembershipInsufficientShares(self):
        data = self.newMemberData('new_member@juntagrico.invalid')
        data.update({'membership': True})
        # ordering with insufficient shares fails
        self.create_paid_share(self.member)  # subscription has enough shares, but membership requires 1
        data.update({'of_member': 0})
        self.assertPost(
            reverse('invitation-new', args=[self.invitee.key]),
            data,
            200,
        )
        self.assertFalse(
            Membership.objects.filter(
                account__email='new_member@juntagrico.invalid'
            ).exists()
        )

    def testAcceptInvitationNewWithMembership(self):
        data = self.newMemberData('new_member@juntagrico.invalid')
        data.update({'membership': True})
        if settings.ENABLE_SHARES:
            # ordering with insufficient shares fails
            self.create_paid_share(self.member)  # subscription has enough shares, but membership requires 1
            data.update({'of_member': 1})
        self.assertPost(
            reverse('invitation-new', args=[self.invitee.key]),
            data,
            302,
        )
        self.assertHasMembership()
        self.assertTrue(
            self.sub.current_members.filter(
                email='new_member@juntagrico.invalid'
            ).exists()
        )
        
    def _acceptInvitationExisting(self, result=302):
        self.assertGet(reverse('invitation', args=[self.invitee.key]), 200)
        self.assertGet(reverse('invitation-existing', args=[self.invitee.key]), 200)

        data = {}
        if settings.ENABLE_SHARES:
            data.update({'of_member': 1})
        self.assertPost(
            reverse('invitation-existing', args=[self.invitee.key]),
            data,
            result,
        )

    def testAcceptInvitationExisting(self):
        self.client.force_login(self.member4.user)
        self._acceptInvitationExisting()
        self.assertTrue(
            self.member4 in self.sub.current_members.all()
        )
        # notification to inviter + welcome + share: admin and member notify
        self.assertEqual(len(mail.outbox), 4 if settings.ENABLE_SHARES else 2)

    def testAcceptInvitationExistingWithOtherPendingSubscription(self):
        self.client.force_login(self.member2.user)
        self._acceptInvitationExisting(200)

    def testAcceptInvitationExistingWithActiveSubscription(self):
        self.client.force_login(self.member3.user)
        self._acceptInvitationExisting(200)
        
    def testAcceptInvitationExistingWithSubscriptionLeavingInFuture(self):
        self.client.force_login(self.member3.user)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        self.member3.subscriptionmembership_set.filter(subscription=self.sub).update(leave_date=tomorrow)
        self._acceptInvitationExisting()
        self.assertTrue(self.member3 in self.sub.future_members)
        self.assertEqual(len(mail.outbox), 4 if settings.ENABLE_SHARES else 2)

    def testRejectInvitation(self):
        self.assertGet(reverse('invitation-reject'), 405)
        self.assertPost(reverse('invitation-reject'), {
            'key': self.invitee.key,
        }, 302)
        self.assertEqual(len(mail.outbox), 1)  # reject notification

    def testInviteeList(self):
        self.client.force_login(self.member.user)
        self.assertGet(reverse('subscription-single', args=[self.sub.pk]), 200)

    def testModifyInvitation(self):
        self.assertGet(reverse('invitation-modify'), 405)
        self.assertPost(
            reverse('invitation-modify'),
            {'key': self.invitee.key, 'action': 'resend'},
            302,
        )
        self.assertEqual(len(mail.outbox), 1)  # invitation resent
        self.assertPost(
            reverse('invitation-modify'),
            {'key': self.invitee.key, 'action': 'resend'},
            302,
        )
        self.assertEqual(len(mail.outbox), 1)  # no additional invitation sent shortly after
        self.assertPost(
            reverse('invitation-modify'),
            {'key': self.invitee.key, 'action': 'withdraw'},
            302,
        )
        with self.assertRaises(Invitee.DoesNotExist):
            self.invitee.refresh_from_db()


@override_settings(MEMBERSHIP={'enable': False})
class InvitationTestsWithoutMembership(InvitationTests):
    def assertHasMembership(self, email='new_member@juntagrico.invalid'):
        # should not create membership if memberships are inactive.
        self.assertFalse(
            Membership.objects.filter(
                account__email=email
            ).exists()
        )

    def testAcceptInvitationNewWithMembershipInsufficientShares(self):
        pass
