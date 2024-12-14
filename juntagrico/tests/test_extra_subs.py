from django.urls import reverse

from . import JuntagricoTestCase


class ExtraSubTests(JuntagricoTestCase):
    fixtures = JuntagricoTestCase.fixtures + ['test/shares']

    def testExtraSubs(self):
        self.assertGet(reverse('extra-change', args=[self.sub.pk]))

        self.assertPost(reverse('extra-change', args=[self.sub.pk]), data={f'amount[{self.extrasub_type.pk}]': 1}, code=302)
