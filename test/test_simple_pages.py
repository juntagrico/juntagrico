from django.urls import reverse

from test.util.test import JuntagricoTestCase


class HomeTests(JuntagricoTestCase):

    def testHome(self):
        self.assertGet(reverse('home'))

    def testCookies(self):
        self.assertGet(reverse('cookies'))

    def testUnpaidSharesInfo(self):
        self.assertGet(reverse('info-unpaid-shares'))
