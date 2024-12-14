import datetime

from django.urls import reverse

from . import JuntagricoTestCase


class ManListTests(JuntagricoTestCase):

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

    def testShareCanceledList(self):
        self.assertGet(reverse('share-mgmt-canceledlist'))
        self.assertGet(reverse('share-mgmt-canceledlist'), member=self.member2, code=302)

    def testShareUnpaindList(self):
        self.assertGet(reverse('manage-share-unpaid'))
        self.assertGet(reverse('manage-share-unpaid'), member=self.member2, code=302)

    def testMemberCanceledList(self):
        self.assertGet(reverse('member-mgmt-canceledlist'))
        self.assertGet(reverse('member-mgmt-canceledlist'), member=self.member2, code=302)

    def testAssignmentList(self):
        self.assertGet(reverse('filter-assignments'))
        self.assertGet(reverse('filter-assignments'), member=self.member2, code=302)

    def testChangeDate(self):
        self.assertGet(reverse('changedate-set'), code=404)
        self.assertPost(reverse('changedate-set'), data={'date': '1970-01-01'}, code=302)
        self.assertEqual(self.client.session['changedate'], datetime.date(1970, 1, 1))
        self.assertGet(reverse('changedate-unset'), code=302)
