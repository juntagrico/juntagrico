from django.urls import reverse

from . import JuntagricoTestCase


class SubAdminTests(JuntagricoTestCase):
    fixtures = JuntagricoTestCase.fixtures + ['test/shares']

    def testSubAdmin(self):
        self.assertGet(reverse('admin:juntagrico_subscription_change', args=(self.sub.pk,)), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_subscription_change', args=(self.sub2.pk,)), member=self.admin)
        self.sub.deactivate()
        self.assertGet(reverse('admin:juntagrico_subscription_change', args=(self.sub.pk,)), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_subscription_changelist'), member=self.admin)
        self.assertGet(reverse('admin:juntagrico_subscription_add'), member=self.admin)
        # Test adding a started subscription without parts and a member that joined before subscription start. Assert that it fails
        data = {
            'depot': str(self.depot.id),
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
            'subscriptionmembership_set-0-join_date': '17.08.2020',
            'subscriptionmembership_set-0-leave_date': '',
            'parts-TOTAL_FORMS': '0',
            'extra_subscription_set-TOTAL_FORMS': '0'
        }
        response = self.assertPost(reverse('admin:juntagrico_subscription_add'), data=data, member=self.admin)
        self.assertListEqual(
            [None, 'missing_part'],  # first code 'part_activation_date_mismatch' reaches here as none somehow
            [e.code for e in response.context_data['errors'].as_data()]
        )
        # Test adding a started subscription with waiting member and unstarted part. Assert that it works
        data = {
            'depot': str(self.depot.id),
            'start_date': '01.01.2021',
            'initial-start_date': '01.01.2021',
            'notes': '',
            'subscriptionmembership_set-TOTAL_FORMS': '1',
            'subscriptionmembership_set-INITIAL_FORMS': '0',
            'subscriptionmembership_set-0-id': '',
            'subscriptionmembership_set-0-subscription': '',
            'subscriptionmembership_set-0-member': str(self.member4.id),
            'subscriptionmembership_set-0-join_date': '',
            'subscriptionmembership_set-0-leave_date': '',
            'parts-TOTAL_FORMS': '1',
            'parts-INITIAL_FORMS': '0',
            'parts-0-id': '',
            'parts-0-subscription': '',
            'parts-0-activation_date': '',
            'parts-0-cancellation_date': '',
            'parts-0-deactivation_date': '',
            'parts-0-type': str(self.sub_type.id),
            'extra_subscription_set-TOTAL_FORMS': '0'
        }
        self.assertPost(reverse('admin:juntagrico_subscription_add'), data=data, member=self.admin, code=302)

    def testSubAdminWithLeftMember(self):
        # Try saving an active subscription, with a member that left it and joined another subscription
        # https://github.com/juntagrico/juntagrico/issues/544
        data = {
            'depot': str(self.depot.id),
            'start_date': '01.01.2017',
            'initial-start_date': '01.01.2017',
            'activation_date': '01.01.2017',
            'notes': '',
            'subscriptionmembership_set-TOTAL_FORMS': '2',
            'subscriptionmembership_set-INITIAL_FORMS': '0',
            'subscriptionmembership_set-0-id': '',
            'subscriptionmembership_set-0-subscription': '',
            'subscriptionmembership_set-0-member': str(self.member.id),
            'subscriptionmembership_set-0-join_date': '01.01.2017',
            'subscriptionmembership_set-0-leave_date': '01.06.2017',
            'subscriptionmembership_set-1-id': '',
            'subscriptionmembership_set-1-subscription': '',
            'subscriptionmembership_set-1-member': str(self.member4.id),
            'subscriptionmembership_set-1-join_date': '01.01.2017',
            'subscriptionmembership_set-1-leave_date': '',
            'parts-TOTAL_FORMS': '1',
            'parts-INITIAL_FORMS': '0',
            'parts-0-id': '',
            'parts-0-subscription': '',
            'parts-0-activation_date': '01.01.2017',
            'parts-0-cancellation_date': '',
            'parts-0-deactivation_date': '',
            'parts-0-type': str(self.sub_type.id),
            'extra_subscription_set-TOTAL_FORMS': '0',
            'extra_subscription_set-INITIAL_FORMS': '0',
        }
        self.assertPost(reverse('admin:juntagrico_subscription_add'), data=data, member=self.admin, code=302)
        # editing that subscription must be possible too
        sub = self.member4.subscription_current
        sub_id = sub.id
        subscription_memberships = sub.subscriptionmembership_set.all().order_by('id')
        data.update({
            'subscriptionmembership_set-INITIAL_FORMS': '2',
            'subscriptionmembership_set-0-id': str(subscription_memberships[0].id),
            'subscriptionmembership_set-0-subscription': str(sub_id),
            'subscriptionmembership_set-1-id': str(subscription_memberships[1].id),
            'subscriptionmembership_set-1-subscription': str(sub_id),
            'extra_subscription_set-INITIAL_FORMS': '1',
            'parts-0-id': str(sub.parts.first().id),
            'parts-0-subscription': str(sub_id),
        })
        self.assertPost(reverse('admin:juntagrico_subscription_change', args=[sub_id]),
                        data=data, member=self.admin, code=302)

    def testWithoutMembership(self):
        data = {
            'depot': str(self.depot.id),
            'start_date': '01.01.2017',
            'initial-start_date': '01.01.2017',
            'activation_date': '01.01.2017',
            'notes': '',
            'subscriptionmembership_set-TOTAL_FORMS': '0',
            'subscriptionmembership_set-INITIAL_FORMS': '0',
            'parts-TOTAL_FORMS': '1',
            'parts-INITIAL_FORMS': '0',
            'parts-0-id': '',
            'parts-0-subscription': '',
            'parts-0-activation_date': '01.01.2017',
            'parts-0-cancellation_date': '',
            'parts-0-deactivation_date': '',
            'parts-0-type': str(self.sub_type3.id),
            'extra_subscription_set-TOTAL_FORMS': '0',
            'extra_subscription_set-INITIAL_FORMS': '0',
        }
        response = self.assertPost(reverse('admin:juntagrico_subscription_add'),
                                   data=data, member=self.admin)
        self.assertListEqual(
            ['require_subscription_membership'],
            [e.code for e in response.context_data['errors'].as_data()]
        )
