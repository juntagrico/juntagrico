from django.contrib import auth
from django.test import TestCase

from test.util.test_data import create_test_data


class CreateSubscriptionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def testSignupLogout(self):
        self.client.force_login(self.member.user)
        user = auth.get_user(self.client)
        assert user.is_authenticated
        self.client.get('/my/signup')
        self.assertEqual(str(auth.get_user(self.client)), 'AnonymousUser')
