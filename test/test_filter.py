from test.util.test import JuntagricoTestCase


class FilterTests(JuntagricoTestCase):

    def testSubscrition(self):
        self.assertSimpleGet('/my/subscriptions')

    def testSubscritionDepot(self):
        url = '/my/subscriptions/depot/'+str(self.depot.pk)+'/'
        self.assertSimpleGet(url)
