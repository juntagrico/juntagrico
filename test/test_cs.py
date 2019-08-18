from django.contrib import auth
from django.test import TestCase
from django.urls import reverse

from test.util.test_data import create_test_data


class CreateSubscriptionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def testSignupLogout(self):
        self.client.force_login(self.member.user)
        user = auth.get_user(self.client)
        assert user.is_authenticated
        self.client.get('/my/signup/')
        self.assertEqual(str(auth.get_user(self.client)), 'AnonymousUser')

    def testRedirect(self):
        response = self.client.get(reverse('cs-subscription'))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('cs-subscription'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('cs-depot'))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('cs-depot'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('cs-start'))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('cs-start'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('cs-co-members'))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('cs-co-members'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('cs-shares'))
        self.assertEqual(response.status_code, 302)
        response = self.client.put(reverse('cs-shares'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('cs-summary'))
        self.assertEqual(response.status_code, 302)
        response = self.client.put(reverse('cs-summary'))
        self.assertEqual(response.status_code, 302)

    def testWelcome(self):
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 302)
