from django.test import TestCase

from test.util.test_data import create_test_data


class FilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def testSubscrition(self):
        self.client.force_login(self.member.user)
        response = self.client.get('/my/subscriptions/')
        self.assertEqual(response.status_code, 200)

    def testSubscritionDepot(self):
        self.client.force_login(self.member.user)
        response = self.client.get('/my/subscriptions/depot/'+str(self.depot.pk)+'/')
        self.assertEqual(response.status_code, 200)
