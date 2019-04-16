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

    def testRedirect(self):
        response =self.client.get('/my/create/subscrition')
        self.assertEqual(response.status_code, 302)
        response =self.client.post('/my/create/subscrition')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/my/create/subscription/selectdepot')
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/my/create/subscription/selectdepot')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/my/create/subscription/start')
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/my/create/subscription/start')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/my/create/subscription/addmembers')
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/my/create/subscription/addmembers')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/my/create/subscription/shares')
        self.assertEqual(response.status_code, 302)
        response = self.client.put('/my/create/subscription/shares')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/my/welcome')
        self.assertEqual(response.status_code, 302)


