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

    def testSubAdmin(self):
        self.assertGet(reverse('admin:juntagrico_subscription_change', args=(self.sub.pk,)), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_subscription_change', args=(self.sub2.pk,)), member=self.admin)
        self.sub.deactivate()
        self.assertGet(reverse('admin:juntagrico_subscription_change', args=(self.sub.pk,)), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_subscription_changelist'), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_subscription_add'), member=self.admin)
        """
        data = {'depot': str(self.depot.id),
                'start_date': '01.01.2021',
                'initial-start_date': '01.01.2021',
                'notes': '',
                'subscriptionmembership_set-TOTAL_FORMS': '1',
                'subscriptionmembership_set-INITIAL_FORMS': '0',
                'subscriptionmembership_set-MIN_NUM_FORMS': '0',
                'subscriptionmembership_set-MAX_NUM_FORMS': '1000',
                'subscriptionmembership_set-0-id': '',
                'subscriptionmembership_set-0-subscription': '',
                'subscriptionmembership_set-0-member': str(self.member4.id),
                'subscriptionmembership_set-0-join_date': '',
                'subscriptionmembership_set-0-leave_date': '',
                'subscriptionmembership_set-__prefix__-id': '',
                'subscriptionmembership_set-__prefix__-subscription': '',
                'subscriptionmembership_set-__prefix__-member': '',
                'subscriptionmembership_set-__prefix__-join_date': '',
                'subscriptionmembership_set-__prefix__-leave_date': '',
                'parts-TOTAL_FORMS': '1',
                'parts-INITIAL_FORMS': '0',
                'parts-MIN_NUM_FORMS': '0',
                'parts-MAX_NUM_FORMS': '1000',
                'parts-0-id': '',
                'parts-0-subscription': '',
                'parts-0-activation_date': '',
                'parts-0-cancellation_date': '',
                'parts-0-deactivation_date': '',
                'parts-0-type': str(self.sub_type.id),
                'parts-__prefix__-id': '',
                'parts-__prefix__-subscription': '',
                'parts-__prefix__-activation_date': '',
                'parts-__prefix__-cancellation_date': '',
                'parts-__prefix__-deactivation_date': '',
                'parts-__prefix__-type': '',
                'extra_subscription_set-TOTAL_FORMS': '0',
                'extra_subscription_set-INITIAL_FORMS': '0',
                'extra_subscription_set-MIN_NUM_FORMS': '0',
                'extra_subscription_set-MAX_NUM_FORMS': '1000',
                'extra_subscription_set-__prefix__-billable_ptr': '',
                'extra_subscription_set-__prefix__-main_subscription': '',
                'extra_subscription_set-__prefix__-activation_date': '',
                'extra_subscription_set-__prefix__-cancellation_date': '',
                'extra_subscription_set-__prefix__-deactivation_date': '',
                'extra_subscription_set-__prefix__-type': '',
                '_save': 'Sichern'} """
        # self.assertPost(reverse('admin:juntagrico_subscription_add'), data=data, member=self.admin, code=302)
        # TODO issue #311

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

    def testShareAdmin(self):
        url = reverse('admin:juntagrico_share_changelist')
        selected_items = [self.share.pk]
        self.assertPost(url, data={'action': 'mark_paid', '_selected_action': selected_items}, member=self.admin,
                        code=302)

    def testSubtypeAdminNoShares(self):
        with self.settings(ENABLE_SHARES=False):
            self.assertGet(reverse('admin:juntagrico_extrasubscriptiontype_change', args=(self.esub_type.pk,)),
                           member=self.admin)
