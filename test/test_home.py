from django.test import TestCase
from django.urls import reverse

from test.util.test_data import create_test_data


class HomeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def testHome(self):
        self.client.force_login(self.member.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
