from django.urls import reverse

from juntagrico.tests import JuntagricoTestCaseWithShares


class SubscriptionTests(JuntagricoTestCaseWithShares):
    def testSubChange(self):
        self.assertGet(reverse('sub-change', args=[self.sub.pk]))
