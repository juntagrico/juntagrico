from django.urls import reverse

from test.util.test import JuntagricoTestCase


class ManListTests(JuntagricoTestCase):

    def testSubWaitingList(self):
        self.assertGet(reverse('sub-mgmt-waitinglist'))

    def testSubCanceledList(self):
        self.assertGet(reverse('sub-mgmt-canceledlist'))

    def testSubChangeList(self):
        self.assertGet(reverse('sub-mgmt-changelist'))

    def testExtraWaitingList(self):
        self.assertGet(reverse('sub-mgmt-extra-waitinglist'))

    def testExtraCanceledList(self):
        self.assertGet(reverse('sub-mgmt-extra-canceledlist'))

    def testShareCanceledList(self):
        self.assertGet(reverse('share-mgmt-canceledlist'))

    def testMemberCanceledList(self):
        self.assertGet(reverse('member-mgmt-canceledlist'))
