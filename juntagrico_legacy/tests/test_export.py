from django.test import tag
from django.urls import reverse

from juntagrico.tests import JuntagricoTestCase


class ExportTests(JuntagricoTestCase):

    def testExport(self):
        self.assertGet(reverse('export'))

    def testMembersfilterExport(self):
        self.assertGet(reverse('export-membersfilter'))

    def testMembersExport(self):
        self.assertGet(reverse('export-members'))

    @tag('shares')
    def testSharesExport(self):
        self.assertGet(reverse('export-shares'))

    def testSubExport(self):
        self.assertGet(reverse('export-subscriptions'))
