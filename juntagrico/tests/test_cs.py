from django.conf import settings
from django.contrib import auth
from django.core import mail
from django.urls import reverse

from juntagrico.entity.depot import Depot
from juntagrico.entity.subtypes import SubscriptionType
from juntagrico.models import Member, Share, Subscription
from . import JuntagricoTestCase
from ..config import Config


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

    def assertGet(self, url, code=200, member=None, **kwargs):
        """ Stay logged out
        """
        response = self.client.get(url, **kwargs)
        self.assertEqual(response.status_code, code)
        return response

    def assertPost(self, url, data=None, code=302, member=None):
        """ Stay logged out
        """
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, code)
        return response

    def assertGetAndPost(self, url, code=302, post_code=302, query=''):
        self.assertGet(reverse(url) + query, code)
        self.assertPost(reverse(url) + query, code=post_code)

    def assertGetAndRedirects(self, get, redirect='subscription-landing'):
        response = self.client.get(reverse(get))
        self.assertRedirects(response, reverse(redirect), fetch_redirect_response=False)

    def addSubToSummary(self, with_co_member=False):
        sub_types_id = SubscriptionType.objects.values_list('id', flat=True)
        response = self.client.post(
            reverse('cs-subscription'),
            {
                f'amount[{type_id}]': 1 if i == 0 else 0
                for i, type_id in enumerate(sub_types_id)
            }
        )
        if self.with_extra_subs:
            self.assertRedirects(response, reverse('cs-extras'))
            self.assertGet(reverse('cs-extras'))
            sub_types_id = SubscriptionType.objects.is_extra().values_list('id', flat=True)
            response = self.client.post(
                reverse('cs-extras'),
                {
                    f'amount[{type_id}]': 1 if i == 0 else 0
                    for i, type_id in enumerate(sub_types_id)
                }
            )
        self.assertRedirects(response, reverse('cs-depot'))
        self.assertGet(reverse('cs-depot'))
        depot_id = Depot.objects.values_list('id', flat=True)[0]
        response = self.client.post(
            reverse('cs-depot'),
            {
                'depot': depot_id,
            }
        )
        self.assertRedirects(response, reverse('cs-start'))
        self.assertGet(reverse('cs-start'))
        response = self.client.post(
            reverse('cs-start'),
            {
                'start_date': '01.01.2020',
                'initial-start_date': '2020-01-01'
            }
        )
        self.assertRedirects(response, reverse('cs-co-members'))
        self.assertGet(reverse('cs-co-members'))

        if with_co_member:
            co_member_data = self.newMemberData('test2@user.com')
            response = self.client.post(reverse('cs-co-members'), co_member_data)
            self.assertRedirects(response, reverse('cs-co-members'))
            self.assertGet(reverse('cs-co-members'))

        response = self.assertGet(reverse('cs-co-members'), 302, data={'next': '1'})
        if Config.enable_shares():
            self.assertRedirects(response, reverse('cs-shares'))
            self.assertGet(reverse('cs-shares'))
            response = self.client.post(
                reverse('cs-shares'),
                {
                    'of_member': 1,
                    'of_co_member[0]': 0,
                }
            )
        self.assertRedirects(response, reverse('cs-summary'))
        # confirm summary
        self.client.get(reverse('cs-summary'))

    def commonAddSub(self, member_email, with_co_member, comment='', comment_in=0):
        initial_share_count = Share.objects.filter(member__email=member_email).count()
        self.addSubToSummary(with_co_member)
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

    def signup(self, with_comment):
        new_member_data = self.newMemberData()
        if with_comment:
            new_member_data['comment'] = 'Short comment'
        response = self.client.post(reverse('signup'), new_member_data)
        self.assertRedirects(response, reverse('cs-subscription'))
        return new_member_data

    def commonSignupTest(self, with_co_member, with_comment=False):
        new_member_data = self.signup(with_comment)
        self.commonAddSub(new_member_data['email'], with_co_member, 'new test comment' if with_comment else '')
        mail_count = 3  # welcome email & 2 admin notifications for new member and new subscription
        if with_co_member:
            mail_count += 2  # Welcome to co-member & admin notification
        if settings.ENABLE_SHARES:
            mail_count += 2  # share email & admin notification
            # no shares are ordered for co-member, thus no more emails
        self.assertEqual(len(mail.outbox), mail_count)

        # signup with different case email address should return form error
        new_member_data['email'] = 'Test@user.com'
        response = self.client.post(reverse('signup'), new_member_data)
        self.assertEqual(response.status_code, 200)

    def testSignupLogout(self):
        self.client.force_login(self.member.user)
        user = auth.get_user(self.client)
        assert user.is_authenticated
        self.client.get(reverse('signup'))
        self.assertEqual(str(auth.get_user(self.client)), 'AnonymousUser')

    def testRedirect(self):
        self.assertGetAndPost('cs-subscription')
        self.assertGetAndPost('cs-extras')
        self.assertGetAndPost('cs-depot')
        self.assertGetAndPost('cs-start')
        self.assertGetAndPost('cs-co-members')
        self.assertGetAndPost('cs-shares')
        self.assertGetAndPost('cs-summary')

    def testWelcome(self):
        self.assertGet(reverse('welcome'))

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
        self.commonAddSub(self.member4.email, True, 'test comment', 3 if settings.ENABLE_SHARES else 1)
        # share mail (if enabled) for member & welcome mail for co-member & 3 admin notifications
        self.assertEqual(len(mail.outbox), 5 if settings.ENABLE_SHARES else 3)

    def testAddSubWithoutComember(self):
        """ test order of new sub by existing member without sub
        """
        self.client.force_login(self.member4.user)
        self.commonAddSub(self.member4.email, False, 'test comment', 2 if settings.ENABLE_SHARES else 0)
        # share mails (if enabled) for member & admin + 1 admin notification on new subscription
        self.assertEqual(len(mail.outbox), 3 if settings.ENABLE_SHARES else 1)

    def testSignupWithComment(self):
        self.commonSignupTest(False, True)

    def testSignupWithoutComment(self):
        self.commonSignupTest(False)

    def testSignupWithCommentAndComember(self):
        self.commonSignupTest(True, True)

    def testSignupWithComember(self):
        self.commonSignupTest(True)

    def testSummaryModificationAndCancel(self):
        self.signup(False)
        self.addSubToSummary(False)
        response = self.assertGet(reverse('signup') + '?mod')
        self.assertDictEqual(response.context_data['form'].data, self.newMemberData())
        self.assertPost(reverse('signup') + '?mod', response.context_data['form'].data)

        self.assertGet(reverse('cs-subscription') + '?mod')
        self.assertGet(reverse('cs-depot') + '?mod')
        self.assertGet(reverse('cs-start') + '?mod')

        self.assertGet(reverse('cs-co-members') + '?mod')
        co_member_data = self.newMemberData('test2@user.com')
        response = self.assertPost(reverse('cs-co-members'), co_member_data)
        self.assertRedirects(response, reverse('cs-summary'))

        self.assertGet(reverse('cs-shares') + '?mod')
        self.assertGet(reverse('cs-cancel'), 302)

    def testSummaryCancel(self):
        with (self.settings(ORGANISATION_WEBSITE={'url': 'https://example.com'})):
            self.signup(False)
            response = self.assertGet(reverse('cs-cancel'), 302)
            self.assertRedirects(response, 'https://example.com', fetch_redirect_response=False)

    def testExternalSignup(self):
        def externalSignupDetails(email='test@user.com', shares = 10, comment='User comment', extra_only = False):
            return {
                'first_name': 'First Name',
                'family_name': 'Last Name',
                'street': 'Street',
                'house_number': '1a',
                'postal_code': '8000',
                'city': 'Zurich',
                'phone': '044',
                'email': email,
                'subscription_id': SubscriptionType.objects.is_extra().values_list('id', flat=True)[0] if extra_only
                    else SubscriptionType.objects.values_list('id', flat=True)[0],
                'depot_id': Depot.objects.values_list('id', flat=True)[0],
                'start_date': '1900-01-01',
                'shares': shares,
                'comment': comment,
                'by_laws_accepted': 'True',
                }
        with self.settings(ENABLE_EXTERNAL_SIGNUP=False):
            self.assertPost(reverse('signup-external'), externalSignupDetails(), code=404)
        with self.settings(ENABLE_EXTERNAL_SIGNUP=True):
            response = self.assertPost(reverse('signup-external'), externalSignupDetails())
            self.assertRedirects(response, reverse('cs-summary'))
            response = self.assertPost(reverse('signup-external'), externalSignupDetails(shares = 0))
            self.assertRedirects(response, reverse('cs-shares'))
            if self.with_extra_subs:
                response = self.assertPost(reverse('signup-external'), externalSignupDetails(extra_only = True))
                self.assertRedirects(response, reverse('cs-subscription'))

class CreateSubscriptionWithoutExtrasTests(CreateSubscriptionTests):
    with_extra_subs = False
