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
        self.assertGet(response.url, member=self.admin)
        self.assertPost(response.url,
                        data={'type': self.job1.type.pk,
                              'slots': self.job1.slots,
                              'multiplier': self.job1.multiplier,
                              'time': '12:00',
                              'start_date': '22.01.2022',
                              'end_date': '30.01.2022',
                              'weekdays': ['1'],
                              'weekly': '7'},
                        member=self.admin, code=302)
        selected_items = [self.job1.pk, self.job2.pk]
        self.assertPost(url, data={'action': 'mass_copy_job', '_selected_action': selected_items}, member=self.admin,
                        code=302)
        # delete job without assignment
        self.assertGet(reverse('admin:juntagrico_recuringjob_delete', args=(self.job1.pk,)), member=self.admin)
        # delete job with assignment (will show a page, that assignments must be deleted first)
        self.assertGet(reverse('admin:juntagrico_recuringjob_delete', args=(self.job2.pk,)), member=self.admin)

    def testPastJobAdmin(self):
        self.assertGet(reverse('admin:juntagrico_recuringjob_change', args=(self.past_job.pk,)), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_recuringjob_change', args=(self.past_job.pk,)), member=self.area_admin)
        self.assertGet(reverse('admin:juntagrico_onetimejob_change', args=(self.past_one_time_job.pk,)), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_onetimejob_change', args=(self.past_one_time_job.pk,)), member=self.area_admin)

    def testDeliveryAdmin(self):
        self.assertGet(reverse('admin:juntagrico_delivery_add'), member=self.admin)
        url = reverse('admin:juntagrico_delivery_changelist')
        self.assertGet(url, member=self.admin)
        selected_items = [self.delivery1.pk]
        response = self.assertPost(url, data={'action': 'copy_delivery', '_selected_action': selected_items},
                                   member=self.admin, code=302)
        self.assertGet(url + response.url, member=self.admin)
        selected_items = [self.delivery1.pk, self.delivery2.pk]
        self.assertPost(url, data={'action': 'copy_delivery', '_selected_action': selected_items}, member=self.admin,
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
        self.assertGet(reverse('admin:juntagrico_member_change', args=(self.member.pk,)), member=self.admin)
        url = reverse('admin:juntagrico_member_changelist')
        self.assertGet(url, member=self.admin)
        selected_items = [self.member.pk]
        self.assertPost(url, data={'action': 'impersonate_job', '_selected_action': selected_items}, member=self.admin,
                        code=302)
        selected_items = [self.member.pk, self.member2.pk]
        self.assertPost(url, data={'action': 'impersonate_job', '_selected_action': selected_items}, member=self.admin,
                        code=302)

    def testSubtypeAdmin(self):
        self.assertGet(reverse('admin:juntagrico_subscriptiontype_change', args=(self.sub_type.pk,)), member=self.admin)

    def testShareAdmin(self):
        url = reverse('admin:juntagrico_share_changelist')
        selected_items = [self.share.pk]
        self.assertPost(url, data={'action': 'mass_edit_share_dates', '_selected_action': selected_items},
                        member=self.admin)

    def testSubtypeAdminNoShares(self):
        with self.settings(ENABLE_SHARES=False):
            self.assertGet(reverse('admin:juntagrico_subscriptiontype_change', args=(self.extrasub_type.pk,)),
                           member=self.admin)
