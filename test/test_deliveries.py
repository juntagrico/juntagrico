from django.urls import reverse

from test.util.test import JuntagricoTestCase


class DeliveryTests(JuntagricoTestCase):

    def testDeliveries(self):
        self.assertGet(reverse('deliveries'))
