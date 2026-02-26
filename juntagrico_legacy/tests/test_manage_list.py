from django.urls import reverse

from juntagrico.tests import JuntagricoTestCase


class ManageListTests(JuntagricoTestCase):
    def testSubWaitingList(self):
        self.assertGet(reverse('sub-mgmt-waitinglist'))
        self.assertGet(reverse('sub-mgmt-waitinglist'), member=self.member2, code=302)

    def testSubCanceledList(self):
        self.assertGet(reverse('sub-mgmt-canceledlist'))
        self.assertGet(reverse('sub-mgmt-canceledlist'), member=self.member2, code=302)

    def testPartWaitingList(self):
        self.assertGet(reverse('sub-mgmt-part-waitinglist'))
        self.assertGet(reverse('sub-mgmt-part-waitinglist'), member=self.member2, code=302)

    def testPartCanceledList(self):
        self.assertGet(reverse('sub-mgmt-part-canceledlist'))
        self.assertGet(reverse('sub-mgmt-part-canceledlist'), member=self.member2, code=302)

    def testExtraWaitingList(self):
        self.assertGet(reverse('sub-mgmt-extra-waitinglist'))
        self.assertGet(reverse('sub-mgmt-extra-waitinglist'), member=self.member2, code=302)

    def testExtraCanceledList(self):
        self.assertGet(reverse('sub-mgmt-extra-canceledlist'))
        self.assertGet(reverse('sub-mgmt-extra-canceledlist'), member=self.member2, code=302)
