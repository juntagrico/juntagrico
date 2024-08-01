import datetime

from django.urls import reverse

from . import JuntagricoTestCase


class ManageListTests(JuntagricoTestCase):

    def testSubscription(self):
        self.assertGet(reverse('manage-subscription'))
        # member2 has no access
        self.assertGet(reverse('manage-subscription'), member=self.member2, code=403)

    def testDepotSubscription(self):
        url = reverse('manage-depot-subs', args=[self.depot.pk])
        self.assertGet(url)
        # member2 has no access
        self.assertGet(url, member=self.member2, code=403)

    def testMember(self):
        self.assertGet(reverse('manage-member'))
        # member2 has no access
        self.assertGet(reverse('manage-member'), member=self.member2, code=403)

    def testAreaMember(self):
        self.assertGet(reverse('manage-area-member', args=[self.area.pk]), code=404)
        self.assertGet(reverse('manage-area-member', args=[self.area.pk]), member=self.area_admin)
        # member2 has no access
        self.assertGet(reverse('manage-area-member', args=[self.area.pk]), member=self.member2, code=403)

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

    def testMemberCanceledList(self):
        self.assertGet(reverse('manage-member-cancelled'))
        self.assertGet(reverse('manage-member-cancelled'), member=self.member2, code=403)

    def testAssignmentList(self):
        self.assertGet(reverse('manage-assignments'))
        self.assertGet(reverse('manage-assignments'), member=self.member2, code=403)

    def testChangeDate(self):
        self.assertGet(reverse('changedate-set'), code=404)
        self.assertPost(reverse('changedate-set'), data={'date': '1970-01-01'}, code=302)
        self.assertEqual(self.client.session['changedate'], datetime.date(1970, 1, 1))
        self.assertGet(reverse('changedate-unset'), code=302)