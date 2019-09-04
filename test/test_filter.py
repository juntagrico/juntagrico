from django.urls import reverse

from test.util.test import JuntagricoTestCase


class FilterTests(JuntagricoTestCase):

    def testSubscrition(self):
        self.assertSimpleGet(reverse('filter-subs'))

    def testSubscritionDepot(self):
        url = reverse('filter-subs-depot', args=[self.depot.pk])
        self.assertSimpleGet(url)
