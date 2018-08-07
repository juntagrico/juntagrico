from django.test import TestCase

from test.util.test_data import create_test_data


class HomeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)


    def testHome(self):
        login = self.client.login(username='test@email.org', password='12345')
        response = self.client.get('/my/home')
        self.assertEqual(response.status_code, 200)


