from django.test import override_settings
from django.urls import reverse

from . import JuntagricoTestCaseWithShares


class ConfigTests(JuntagricoTestCaseWithShares):
    def testOverview(self):
        self.assertGet(reverse('config'), 200)
        self.assertGet(reverse('config'), 200, self.admin)
        self.assertGet(reverse('config'), 302, self.member2)


@override_settings(ASSIGNMENT_UNIT='HOURS')
class ConfigWithHours(ConfigTests):
    pass
