from django.urls import reverse

from test.util.test import JuntagricoTestCase


class ISO2002Tests(JuntagricoTestCase):

    def testSharePAIN001(self):
        self.assertPost(reverse('share-pain001'), data={'share_ids': str(self.share.pk)})

    def testSharePAIN001404(self):
        self.assertGet(reverse('share-pain001'), code=404)
