from django.urls import reverse

from juntagrico.entity.share import Share
from test.util.test import JuntagricoTestCase


class JobTests(JuntagricoTestCase):

    def testSub(self):
        self.assertSimpleGet(reverse('sub-detail'))
        self.assertSimpleGet(reverse('sub-detail-id', args=[self.sub.pk]))

    def testSubChange(self):
        self.assertSimpleGet(reverse('sub-change', args=[self.sub.pk]))

    def testDepotChange(self):
        self.assertSimpleGet(reverse('depot-change', args=[self.sub.pk]))
        self.assertSimplePost(reverse('depot-change', args=[self.sub.pk]), {'depot': self.depot2.pk})
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.future_depot, self.depot2)

    def testSizeChange(self):
        with self.settings(BUSINESS_YEAR_CANCELATION_MONTH=12):
            self.assertSimpleGet(reverse('size-change', args=[self.sub.pk]))
            self.assertSimplePost(reverse('size-change', args=[self.sub.pk]), {'amount[' + str(self.sub_type2.pk) + ']': 1})
            self.sub.refresh_from_db()
            self.assertEqual(self.sub.future_types.all()[0], self.sub_type)
            self.assertEqual(self.sub.future_types.count(), 1)
            Share.objects.create(**self.share_data)
            self.assertSimplePost(reverse('size-change', args=[self.sub.pk]), {'amount[' + str(self.sub_type2.pk) + ']': 1})
            self.sub.refresh_from_db()
            self.assertEqual(self.sub.future_types.all()[0], self.sub_type2)
            self.assertEqual(self.sub.future_types.count(), 1)
