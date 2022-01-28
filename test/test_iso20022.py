from django.urls import reverse

from test.util.test import JuntagricoTestCase


class ISO2002Tests(JuntagricoTestCase):

    def setUp(self):
        super().setUp()
        # add iban to member such that tested share can be paid back.
        self.member.iban = 'CH6189144414396247884'
        self.member.save()

    def testSharePAIN001(self):
        self.assertPost(reverse('share-pain001'), data={'share_ids': str(self.share.pk)})

    def testSharePAIN001404(self):
        self.assertGet(reverse('share-pain001'), code=404)
