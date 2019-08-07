from django.test import TestCase
from django.urls import reverse

from test.util.test import test_simple_get
from test.util.test_data import create_test_data


class FilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def testSubscrition(self):
        self.client.force_login(self.member.user)
        response = self.client.get(reverse('subs'))
        self.assertEqual(response.status_code, 200)

    def testSubscritionDepot(self):
        url = reverse('subs-depot', args=[self.depot.pk])
        test_simple_get(self, url)
