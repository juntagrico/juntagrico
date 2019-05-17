from juntagrico.entity.share import Share
from test.util.test import JuntagricoTestCase


class JobTests(JuntagricoTestCase):

    def testSub(self):
        self.assertSimpleGet('/my/subscription/detail/')
        self.assertSimpleGet('/my/subscription/detail/' + str(self.sub.pk) + '/')

    def testSubChange(self):
        self.assertSimpleGet('/my/subscription/change/overview/' + str(self.sub.pk) + '/')

    def testDepotChange(self):
        self.assertSimpleGet('/my/subscription/change/depot/' + str(self.sub.pk) + '/')
        self.assertSimplePost('/my/subscription/change/depot/' + str(self.sub.pk) + '/', {'depot': self.depot2.pk})
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.future_depot, self.depot2)

    def testSizeChange(self):
        self.assertSimpleGet('/my/subscription/change/size/' + str(self.sub.pk) + '/')
        self.assertSimplePost('/my/subscription/change/size/' + str(self.sub.pk) + '/', {'subscription': self.sub_type2.pk})
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.future_types.all()[0], self.sub_type)
        self.assertEqual(self.sub.future_types.count(), 1)
        Share.objects.create(**self.share_data)
        self.assertSimplePost('/my/subscription/change/size/' + str(self.sub.pk) + '/', {'subscription': self.sub_type2.pk})
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.future_types.all()[0], self.sub_type2)
        self.assertEqual(self.sub.future_types.count(), 1)
