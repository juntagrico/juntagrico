from django.urls import reverse

from . import JuntagricoTestCase


class ManageSubPendingListTests(JuntagricoTestCase):
    def testSubscriptionPendingList(self):
        response = self.assertGet(reverse('manage-sub-pending'))
        # check that list is correct
        objects = response.context['object_list']
        self.assertEqual(set(objects.order_by('id')), {self.cancelled_sub, self.sub2})
        # member2 has no access
        self.assertGet(reverse('manage-sub-pending'), member=self.member2, code=403)

    def testSubscriptionActivate(self):
        self.assertGet(reverse('parts-apply'), code=302)
        # member2 has no access
        self.assertPost(reverse('parts-apply'), member=self.member2, code=302)
        self.assertFalse(self.sub2.parts.first().active)
        # test activation
        part = self.sub2.parts.first()
        self.assertPost(reverse('parts-apply'), {'parts[]': [part.id]}, code=302)
        # check that part is active
        part.refresh_from_db()
        self.assertTrue(part.active)

    def testSubscriptionDeactivate(self):
        self.assertGet(reverse('parts-apply'), code=302)
        self.assertTrue(self.cancelled_sub.parts.first().active)
        # test deactivate
        part = self.cancelled_sub.parts.first()
        self.assertPost(reverse('parts-apply'), {'parts[]': [part.id]}, code=302)
        # check that part is deactivated
        part.refresh_from_db()
        self.assertFalse(part.active)


class ManageSubRecentListTests(JuntagricoTestCase):
    def testSubscriptionRecentList(self):
        response = self.assertGet(reverse('manage-sub-recent'))
        # check that list is correct
        self.assertEqual(set(response.context['ordered_parts']), {
            *self.sub3.parts.all(), *self.sub.parts.all(), *self.sub2.parts.all(), *self.cancelled_sub.parts.all()
        })
        self.assertEqual(set(response.context['activated_parts']), {
            *self.sub3.parts.all(), *self.sub.parts.all(), *self.cancelled_sub.parts.all()
        })
        self.assertEqual(set(response.context['cancelled_parts']), {
            *self.sub3.parts.all(), *self.cancelled_sub.parts.all()
        })
        self.assertEqual(set(response.context['deactivated_parts']), {
            *self.sub3.parts.all()
        })
        self.assertEqual(set(response.context['joined_memberships']), {
            *self.sub3.subscriptionmembership_set.all(), *self.sub.subscriptionmembership_set.all(),
            *self.cancelled_sub.subscriptionmembership_set.all()
        })
        self.assertEqual(set(response.context['left_memberships']), {
            *self.sub3.subscriptionmembership_set.all()
        })
        # member2 has no access
        self.assertGet(reverse('manage-sub-recent'), member=self.member2, code=403)
