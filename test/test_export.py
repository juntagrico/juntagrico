from django.urls import reverse

from test.util.test import JuntagricoTestCase


class ExportTests(JuntagricoTestCase):

    def testExport(self):
        self.assertGet(reverse('export'))

    def testMembersfilterExport(self):
        self.assertGet(reverse('export-membersfilter'))

    def testMembersExport(self):
        self.assertGet(reverse('export-members'))

    def testSharesExport(self):
        self.assertGet(reverse('export-shares'))
