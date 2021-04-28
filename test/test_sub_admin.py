from django.urls import reverse

from test.util.test import JuntagricoTestCase


class SubAdminTests(JuntagricoTestCase):

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
                'initial-start_date': '2021-01-01',
                'notes': '',
                'subscriptionmembership_set-TOTAL_FORMS': '1',
                'subscriptionmembership_set-INITIAL_FORMS': '0',
                'subscriptionmembership_set-MIN_NUM_FORMS': '0',
                'subscriptionmembership_set-MAX_NUM_FORMS': '1000',
                'subscriptionmembership_set-0-id': '',
                'subscriptionmembership_set-0-subscription': '',
                'subscriptionmembership_set-0-member': str(self.member4.id),
                'subscriptionmembership_set-0-join_date': '17.08.2020',
                'initial-subscriptionmembership_set-0-join_date': '2020-08-17+08%3A26%3A43%2B00%3A00',
                'subscriptionmembership_set-0-leave_date': '',
                'subscriptionmembership_set-__prefix__-id': '',
                'subscriptionmembership_set-__prefix__-subscription': '',
                'subscriptionmembership_set-__prefix__-member': '',
                'subscriptionmembership_set-__prefix__-join_date': '17.08.2020',
                'initial-subscriptionmembership_set-__prefix__-join_date': '2020-08-17+08%3A26%3A43%2B00%3A00',
                'subscriptionmembership_set-__prefix__-leave_date': '',
                'parts-TOTAL_FORMS': '0',
                'parts-INITIAL_FORMS': '0',
                'parts-MIN_NUM_FORMS': '0',
                'parts-MAX_NUM_FORMS': '1000',
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
                'extra_subscription_set-__prefix__-type': '', }
                """
        # self.assertPost(reverse('admin:juntagrico_subscription_add'), data=data, member=self.admin)
        # TODO issue #311
        """
        data = {'depot': str(self.depot.id),
                'start_date': '01.01.2021',
                'initial-start_date': '2021-01-01',
                'notes': '',
                'subscriptionmembership_set-TOTAL_FORMS': '1',
                'subscriptionmembership_set-INITIAL_FORMS': '0',
                'subscriptionmembership_set-MIN_NUM_FORMS': '0',
                'subscriptionmembership_set-MAX_NUM_FORMS': '1000',
                'subscriptionmembership_set-0-id': '',
                'subscriptionmembership_set-0-subscription': '',
                'subscriptionmembership_set-0-member': str(self.member4.id),
                'subscriptionmembership_set-0-join_date': '',
                'initial-subscriptionmembership_set-0-join_date': '',
                'subscriptionmembership_set-0-leave_date': '',
                'subscriptionmembership_set-__prefix__-id': '',
                'subscriptionmembership_set-__prefix__-subscription': '',
                'subscriptionmembership_set-__prefix__-member': '',
                'subscriptionmembership_set-__prefix__-join_date': '',
                'initial-subscriptionmembership_set-__prefix__-join_date': '',
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
                'extra_subscription_set-__prefix__-type': '', }
        """
        # self.assertPost(reverse('admin:juntagrico_subscription_add'), data=data, member=self.admin, code=302)
        # TODO issue #311
