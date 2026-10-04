from django.test import override_settings
from django.urls import reverse

from . import JuntagricoTestCase


class HomeTests(JuntagricoTestCase):

    def testHome(self):
        self.assertGet(reverse('home'))
        self.assertGet(reverse('home'), member=self.member2)
        self.assertGet(reverse('home'), member=self.member3)
        self.assertGet(reverse('home'), member=self.member4)
        self.assertGet(reverse('home'), member=self.admin)

    @override_settings(
        JOBS_FRONTPAGE={
            'days': 0,
            'min': 0,
            'promoted_types': ['nameot'],
        }
    )
    def testHomePromotedJobs(self):
        response = self.assertGet(reverse('home'))
        self.assertContains(response, 'area_location1')

    def testCookies(self):
        self.assertGet(reverse('cookies'))

    def testUnpaidSharesInfo(self):
        self.assertGet(reverse('info-unpaid-shares'))
