from django.urls import reverse

from juntagrico.entity.jobs import Assignment
from test.util.test import JuntagricoTestCase


class AdminTests(JuntagricoTestCase):

    def testOneTimeJobAdmin(self):
        self.assertGet(reverse('admin:juntagrico_onetimejob_change', args=(self.one_time_job1.pk,)), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_onetimejob_change', args=(self.one_time_job1.pk,)),
                       member=self.area_admin)
        url = reverse('admin:juntagrico_onetimejob_changelist')
        self.assertGet(url, member=self.admin)
        selected_items = [self.one_time_job1.pk]
        Assignment.objects.create(job=self.one_time_job1, member=self.member, amount=1.0)
        self.assertPost(url, data={'action': 'transform_job', '_selected_action': selected_items}, member=self.admin,
                        code=302)

    def testJobAdmin(self):
        self.assertGet(reverse('admin:juntagrico_recuringjob_change', args=(self.job1.pk,)), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_recuringjob_change', args=(self.job1.pk,)), member=self.area_admin)
        self.assertGet(reverse('admin:juntagrico_recuringjob_add'), member=self.admin)
        url = reverse('admin:juntagrico_recuringjob_changelist')
        self.assertGet(url, member=self.admin)
        selected_items = [self.job1.pk]
        self.assertPost(url, data={'action': 'copy_job', '_selected_action': selected_items}, member=self.admin,
                        code=302)
        response = self.assertPost(url, data={'action': 'mass_copy_job', '_selected_action': selected_items},
                                   member=self.admin, code=302)
        self.assertGet(url + response.url, member=self.admin)
        selected_items = [self.job1.pk, self.job2.pk]
        self.assertPost(url, data={'action': 'mass_copy_job', '_selected_action': selected_items}, member=self.admin,
                        code=302)

    def testJobTypeAdmin(self):
        self.assertGet(reverse('admin:juntagrico_jobtype_change', args=(self.job1.type.pk,)), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_jobtype_change', args=(self.job1.type.pk,)), member=self.area_admin)
        url = reverse('admin:juntagrico_jobtype_changelist')
        selected_items = [self.job_type.pk]
        self.assertPost(url, data={'action': 'transform_job_type', '_selected_action': selected_items},
                        member=self.admin, code=302)

    def testAreaAdmin(self):
        self.assertGet(reverse('admin:juntagrico_activityarea_change', args=(self.area.pk,)), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_activityarea_change', args=(self.area.pk,)), member=self.area_admin)

    def testAssignmentAdmin(self):
        self.assertGet(reverse('admin:juntagrico_assignment_change', args=(self.assignment.pk,)), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_assignment_change', args=(self.assignment.pk,)),
                       member=self.area_admin)

    def testMemberAdmin(self):
        def raw_id_url(url, name, subscription_id):
            return '{}?qs_name={}&sub_id={}'.format(url, name, str(subscription_id))
        self.assertGet(reverse('admin:juntagrico_member_change', args=(self.member.pk,)), member=self.admin)
        url = reverse('admin:juntagrico_member_changelist')
        self.assertGet(url, member=self.admin)
        selected_items = [self.member.pk]
        self.assertPost(url, data={'action': 'impersonate_job', '_selected_action': selected_items}, member=self.admin,
                        code=302)
        selected_items = [self.member.pk, self.member2.pk]
        self.assertPost(url, data={'action': 'impersonate_job', '_selected_action': selected_items}, member=self.admin,
                        code=302)
        cs_url = raw_id_url(url, 'cs', '')
        self.assertGet(cs_url, member=self.admin)
        s_url = raw_id_url(url, 's', self.sub.pk)
        self.assertGet(s_url, member=self.admin)
        fs_url = raw_id_url(url, 'fs', self.sub.pk)
        self.assertGet(fs_url, member=self.admin)
        all_url = raw_id_url(url, 'all', '')
        self.assertGet(all_url, member=self.admin)

    def testSubtypeAdmin(self):
        self.assertGet(reverse('admin:juntagrico_subscriptiontype_change', args=(self.sub_type.pk,)), member=self.admin)

    def testSubtypeAdminNoShares(self):
        with self.settings(ENABLE_SHARES=False):
            self.assertGet(reverse('admin:juntagrico_extrasubscriptiontype_change', args=(self.esub_type.pk,)),
                           member=self.admin)
