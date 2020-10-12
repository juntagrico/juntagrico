from django.urls import reverse

from test.util.test import JuntagricoTestCase


class ExtraSubTests(JuntagricoTestCase):

    def testExtraSubs(self):
        self.assertGet(reverse('extra-change', args=[self.sub.pk]))

        self.assertPost(reverse('extra-change', args=[self.sub.pk]), data={'extra' + str(self.esub_type.pk): 1}, code=302)
