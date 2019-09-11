from django.urls import reverse

from test.util.test import JuntagricoTestCase


class ISO2002Tests(JuntagricoTestCase):

    def testSharePAIN001(self):
        self.assertGet(reverse('home'))
