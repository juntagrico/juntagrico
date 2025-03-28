from django.test import tag
from django.urls import reverse

from . import JuntagricoTestCase


class ExportTests(JuntagricoTestCase):

    def get_data(self, resource=0, file_format=0, selected=None):
        data = {
            "resource": resource,
            "format": file_format,
            "export_start_date_day": "1",
            "export_start_date_month": "1",
            "export_start_date_year": "2024",
            "export_end_date_day": "31",
            "export_end_date_month": "12",
            "export_end_date_year": "2024"
        }
        if selected:
            data.update({f: "on" for f in selected})
        return data

    def testExport(self):
        self.assertGet(reverse('export'))

    def testMembersfilterExport(self):
        self.assertGet(reverse('export-membersfilter'))
        # member does not have view permission on member model
        export_url = reverse('admin:juntagrico_member_export')
        self.assertGet(export_url, 403)
        # admin can access
        response = self.assertGet(export_url, member=self.admin)
        fields = response.context_data['form'].resource_fields['MemberWithAssignmentsAndAreaResource']
        response = self.assertPost(export_url, member=self.admin, data=self.get_data(1, selected=fields))
        self.assertEqual(response.headers['Content-Type'], 'text/csv')

    def testMembersExport(self):
        self.assertGet(reverse('export-members'))
        export_url = reverse('admin:juntagrico_member_export')
        response = self.assertGet(export_url, member=self.admin)
        fields = response.context_data['form'].resource_fields['MemberResource']
        response = self.assertPost(export_url, member=self.admin, data=self.get_data(selected=fields))
        self.assertEqual(response.headers['Content-Type'], 'text/csv')

    def testMemberAssignmentsPerAreaExport(self):
        export_url = reverse('admin:juntagrico_member_export')
        response = self.assertGet(export_url, member=self.admin)
        fields = response.context_data['form'].resource_fields['MemberAssignmentsPerArea']
        response = self.assertPost(export_url, member=self.admin, data=self.get_data(2, selected=fields))
        self.assertEqual(response.headers['Content-Type'], 'text/csv')

    @tag('shares')
    def testSharesExport(self):
        self.assertGet(reverse('export-shares'))
        export_url = reverse('admin:juntagrico_share_export')
        response = self.assertGet(export_url, member=self.admin)
        fields = response.context_data['form'].resource_fields['ShareResource']
        response = self.assertPost(export_url, member=self.admin, data={
            "format": "0",
            **{f: "on" for f in fields}
        })
        self.assertEqual(response.headers['Content-Type'], 'text/csv')

    def testSubExport(self):
        self.assertGet(reverse('export-subscriptions'))
        export_url = reverse('admin:juntagrico_subscription_export')
        response = self.assertGet(export_url, member=self.admin)
        fields = response.context_data['form'].resource_fields
        response = self.assertPost(export_url, member=self.admin,
                                   data=self.get_data(selected=fields['SubscriptionResource']))
        self.assertEqual(response.headers['Content-Type'], 'text/csv')
        response = self.assertPost(export_url, member=self.admin,
                                   data=self.get_data(1, selected=fields['SubscriptionPartResource']))
        self.assertEqual(response.headers['Content-Type'], 'text/csv')
