from django.test import tag
from django.urls import reverse

from . import JuntagricoTestCase


class ExportTests(JuntagricoTestCase):

    def get_data(self, resource=0, file_format=0):
        return {
            "resource": resource,
            "file_format": file_format,
            "start_date_day": "1",
            "start_date_month": "1",
            "start_date_year": "2024",
            "end_date_day": "31",
            "end_date_month": "12",
            "end_date_year": "2024"
        }

    def testExport(self):
        self.assertGet(reverse('export'))

    def testMembersfilterExport(self):
        self.assertGet(reverse('export-membersfilter'))
        # member does not have view permission on member model
        export_url = reverse('admin:juntagrico_member_export')
        self.assertGet(export_url, 403)
        # admin can access
        self.assertGet(export_url, member=self.admin)
        response = self.assertPost(export_url, member=self.admin, data=self.get_data(1))
        self.assertEqual(response.headers['Content-Type'], 'text/csv')

    def testMembersExport(self):
        self.assertGet(reverse('export-members'))
        export_url = reverse('admin:juntagrico_member_export')
        self.assertGet(export_url, member=self.admin)
        response = self.assertPost(export_url, member=self.admin, data=self.get_data())
        self.assertEqual(response.headers['Content-Type'], 'text/csv')

    def testMemberAssignmentsPerAreaExport(self):
        export_url = reverse('admin:juntagrico_member_export')
        self.assertGet(export_url, member=self.admin)
        response = self.assertPost(export_url, member=self.admin, data=self.get_data(2))
        self.assertEqual(response.headers['Content-Type'], 'text/csv')

    @tag('shares')
    def testSharesExport(self):
        self.assertGet(reverse('export-shares'))
        export_url = reverse('admin:juntagrico_share_export')
        self.assertGet(export_url, member=self.admin)
        response = self.assertPost(export_url, member=self.admin, data={
            "file_format": "0",
        })
        self.assertEqual(response.headers['Content-Type'], 'text/csv')

    def testSubExport(self):
        self.assertGet(reverse('export-subscriptions'))
        export_url = reverse('admin:juntagrico_subscription_export')
        self.assertGet(export_url, member=self.admin)
        response = self.assertPost(export_url, member=self.admin, data=self.get_data())
        self.assertEqual(response.headers['Content-Type'], 'text/csv')
        response = self.assertPost(export_url, member=self.admin, data=self.get_data(1))
        self.assertEqual(response.headers['Content-Type'], 'text/csv')
