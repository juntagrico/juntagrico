from django.urls import reverse

from test.util.test import JuntagricoTestCase


class FilterTests(JuntagricoTestCase):

    def testSubscrition(self):
        self.assertGet(reverse('filter-subs'))
        self.assertGet(reverse('filter-subs'), member=self.member2, code=302)

    def testSubscritionDepot(self):
        url = reverse('filter-subs-depot', args=[self.depot.pk])
        self.assertGet(url)
        self.assertGet(url, member=self.member2, code=302)

    def testFilter(self):
        self.assertGet(reverse('filters'))
        self.assertGet(reverse('filters'), member=self.member2, code=302)

    def testAreaFilter(self):
        self.assertGet(reverse('filter-area', args=[self.area.pk]), code=404)
        self.assertGet(reverse('filter-area', args=[self.area.pk]), member=self.area_admin)
        self.assertGet(reverse('filter-area', args=[self.area.pk]), member=self.member2, code=302)

    def testDepotFilter(self):
        self.assertGet(reverse('filter-depot', args=[self.depot.pk]))
        self.assertGet(reverse('filter-depot', args=[self.depot.pk]), member=self.member2, code=302)
