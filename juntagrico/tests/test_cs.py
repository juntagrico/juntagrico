from django.conf import settings
from django.contrib import auth
from django.core import mail
from django.urls import reverse

from juntagrico.entity.depot import Depot
from juntagrico.entity.subtypes import SubscriptionType
from juntagrico.models import Member, Share, Subscription
from . import JuntagricoTestCase


class CreateSubscriptionTests(JuntagricoTestCase):
    @staticmethod
    def newMemberData(email='test@user.com'):
        return {
            'last_name': 'Last Name',
            'first_name': 'First Name',
            'addr_street': 'Street',
            'addr_zipcode': '8000',
            'addr_location': 'Zurich',
            'phone': '044',
            'mobile_phone': '',
            'email': email,
            'birthday': '',
            'agb': 'on'
        }

    def assertGet(self, url, code=302, member=None):
        """ Stay logged out
        """
        response = self.client.get(url)
        self.assertEqual(response.status_code, code)
        return response

    def assertPost(self, url, data=None, code=302, member=None):
        """ Stay logged out
        """
        response = self.client.post(url)
        self.assertEqual(response.status_code, code)
        return response

    def assertGetAndPost(self, url, code=302):
        self.assertGet(reverse(url), code)
        self.assertPost(reverse(url), code)

    def assertGetAndRedirects(self, get, redirect='subscription-landing'):
        response = self.client.get(reverse(get))
        self.assertRedirects(response, reverse(redirect), fetch_redirect_response=False)

    def commonAddSub(self, member_email, comment='', comment_in=0):
        initial_share_count = Share.objects.filter(member__email=member_email).count()
        sub_types_id = SubscriptionType.objects.values_list('id', flat=True)
        response = self.client.post(
            reverse('cs-subscription'),
            {
                f'amount[{type_id}]': 1 if i == 0 else 0
                for i, type_id in enumerate(sub_types_id)
            }
        )
        self.assertRedirects(response, reverse('cs-depot'))
        depot_id = Depot.objects.values_list('id', flat=True)
        response = self.client.post(
            reverse('cs-depot'),
            {
                'depot': depot_id[0],
            }
        )
        self.assertRedirects(response, reverse('cs-start'))
        response = self.client.post(
            reverse('cs-start'),
            {
                'start_date': '01.01.2020',
                'initial-start_date': '2020-01-01'
            }
        )
        self.assertRedirects(response, reverse('cs-co-members'))
        co_member_data = self.newMemberData('test2@user.com')
        response = self.client.post(reverse('cs-co-members'), co_member_data)
        self.assertRedirects(response, reverse('cs-co-members'))
        self.assertGet(reverse('cs-shares'), 200)
        response = self.client.post(
            reverse('cs-shares'),
            {
                'shares_mainmember': 1
            }
        )
        self.assertRedirects(response, reverse('cs-summary'))
        # confirm summary
        response = self.client.post(reverse('cs-summary'), {'comment': comment})
        self.assertRedirects(response, reverse('welcome-with-sub'))
        self.assertEqual(Member.objects.filter(email=member_email).count(), 1)
        if settings.ENABLE_SHARES:
            self.assertEqual(Share.objects.filter(member__email=member_email).count(), initial_share_count + 1)
        subscription = Subscription.objects.filter(primary_member__email=member_email).first()
        self.assertNotEqual(subscription, None)
        # look for comment in admin notification
        self.assertIn(comment, mail.outbox[comment_in].body)
        self.assertEqual(subscription.primary_member.signup_comment, comment)

    def commonSignupTest(self, with_comment=False):
        new_member_data = self.newMemberData()
        if with_comment:
            new_member_data['comment'] = 'Short comment'
        response = self.client.post(reverse('signup'), new_member_data)
        self.assertRedirects(response, reverse('cs-subscription'))
        self.commonAddSub(new_member_data['email'], 'new test comment' if with_comment else '')
        # welcome mail, share mail & same for co-member & 3 admin notifications
        self.assertEqual(len(mail.outbox), 7 if settings.ENABLE_SHARES else 5)

        # signup with different case email address should fail
        new_member_data['email'] = 'Test@user.com'
        response = self.client.post(reverse('signup'), new_member_data)
        self.assertEqual(response.status_code, 200)  # no redirect = failed

    def testSignupLogout(self):
        self.client.force_login(self.member.user)
        user = auth.get_user(self.client)
        assert user.is_authenticated
        self.client.get(reverse('signup'))
        self.assertEqual(str(auth.get_user(self.client)), 'AnonymousUser')

    def testRedirect(self):
        self.assertGetAndPost('cs-subscription')
        self.assertGetAndPost('cs-depot')
        self.assertGetAndPost('cs-start')
        self.assertGetAndPost('cs-co-members')
        self.assertGetAndPost('cs-shares')
        self.assertGetAndPost('cs-summary')

    def testWelcome(self):
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)

    def testAddSubWithExistingSub(self):
        """ subscription creation form should be inaccessible, for members with a subscription
        """
        self.client.force_login(self.member.user)
        self.assertGetAndRedirects('cs-subscription')
        self.assertGetAndRedirects('cs-depot')
        self.assertGetAndRedirects('cs-start')
        self.assertGetAndRedirects('cs-co-members')
        self.assertGetAndRedirects('cs-shares')
        self.assertGetAndRedirects('cs-summary')

    def testAddSub(self):
        """ test order of new sub by existing member without sub
        """
        self.client.force_login(self.member4.user)
        self.commonAddSub(self.member4.email, 'test comment', 2 if settings.ENABLE_SHARES else 0)
        # share mail (if enabled) for member & welcome mail for co-member & 3 admin notifications
        self.assertEqual(len(mail.outbox), 5 if settings.ENABLE_SHARES else 3)

    def testSignupWithComment(self):
        self.commonSignupTest(True)

    def testSignupWithoutComment(self):
        self.commonSignupTest()
