from django.urls import reverse

from test.util.test import JuntagricoTestCase


class ManListTests(JuntagricoTestCase):

    def testSubWaitingList(self):
        self.assertGet(reverse('sub-mgmt-waitinglist'))
        self.assertGet(reverse('sub-mgmt-waitinglist'), member=self.member2, code=302)

    def testSubCanceledList(self):
        self.assertGet(reverse('sub-mgmt-canceledlist'))
        self.assertGet(reverse('sub-mgmt-canceledlist'), member=self.member2, code=302)

    def testSubChangeList(self):
        self.assertGet(reverse('sub-mgmt-changelist'))
        self.assertGet(reverse('sub-mgmt-changelist'), member=self.member2, code=302)

    def testExtraWaitingList(self):
        self.assertGet(reverse('sub-mgmt-extra-waitinglist'))
        self.assertGet(reverse('sub-mgmt-extra-waitinglist'), member=self.member2, code=302)

    def testExtraCanceledList(self):
        self.assertGet(reverse('sub-mgmt-extra-canceledlist'))
        self.assertGet(reverse('sub-mgmt-extra-canceledlist'), member=self.member2, code=302)

    def testShareCanceledList(self):
        self.assertGet(reverse('share-mgmt-canceledlist'))
        self.assertGet(reverse('share-mgmt-canceledlist'), member=self.member2, code=302)

    def testMemberCanceledList(self):
        self.assertGet(reverse('member-mgmt-canceledlist'))
        self.assertGet(reverse('member-mgmt-canceledlist'), member=self.member2, code=302)

    def testChangeDate(self):
        self.assertGet(reverse('changedate-set'), code=404)
        self.assertPost(reverse('changedate-set'), data={'date': '01/01/1970'}, code=302)
        self.assertPost(reverse('changedate-set'), member=self.member2, code=302)
        self.assertGet(reverse('changedate-unset'), code=302)
        self.assertGet(reverse('changedate-unset'), member=self.member2, code=302)
