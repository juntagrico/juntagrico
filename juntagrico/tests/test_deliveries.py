from django.urls import reverse

from . import JuntagricoTestCase


class DeliveryTests(JuntagricoTestCase):

    def testDeliveries(self):
        self.assertGet(reverse('deliveries'))
