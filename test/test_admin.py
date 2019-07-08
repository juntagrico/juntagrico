from django.test import TestCase

from test.util.test_data import create_test_data
from django.urls import reverse


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def testOneTimeJobAdmin(self):
        self.client.force_login(self.admin.user)
        response = self.client.get(reverse('admin:juntagrico_onetimejob_change', args=(self.one_time_job1.pk,)))
        self.assertEqual(response.status_code, 200)

    def testJobAdmin(self):
        self.client.force_login(self.admin.user)
        response = self.client.get(reverse('admin:juntagrico_recuringjob_change', args=(self.job1.pk,)))
        self.assertEqual(response.status_code, 200)
