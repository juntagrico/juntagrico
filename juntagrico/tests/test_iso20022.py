from django.test import tag
from django.urls import reverse

from . import JuntagricoTestCase


@tag('shares')
class ISO2002Tests(JuntagricoTestCase):
    fixtures = JuntagricoTestCase.fixtures + ['test/shares']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # add iban to member such that tested share can be paid back.
        cls.member.iban = 'CH6189144414396247884'
        cls.member.save()

    def testSharePAIN001(self):
        self.assertPost(reverse('share-pain001'), data={'share_ids': str(self.member.share_set.first().pk)})

    def testSharePAIN001404(self):
        self.assertGet(reverse('share-pain001'), code=404)
