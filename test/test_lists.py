from django.urls import reverse

from test.util.test import JuntagricoTestCase


class ListTests(JuntagricoTestCase):

    def testDepotList(self):
        self.assertGet(reverse('lists-depotlist'))
        self.assertGet(reverse('lists-depotlist'), member=self.member2, code=302)

    def testDepotOverview(self):
        self.assertGet(reverse('lists-depot-overview'))
        self.assertGet(reverse('lists-depot-overview'), member=self.member2, code=302)

    def testAmountOverView(self):
        self.assertGet(reverse('lists-depot-amountoverview'))
        self.assertGet(reverse('lists-depot-amountoverview'), member=self.member2, code=302)
