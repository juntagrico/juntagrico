from django.urls import reverse

from . import JuntagricoTestCase


class ManageSubPendingListTests(JuntagricoTestCase):

    def testSubscriptionWaiting(self):
        response = self.assertGet(reverse('manage-sub-pending'))
        # check that member list is correct
        objects = response.context['object_list']
        self.assertEqual(list(objects.order_by('id')), [
            self.sub2
        ])
        # member2 has no access
        self.assertGet(reverse('manage-sub-pending'), member=self.member2, code=403)

    def testSubscriptionActivate(self):
        self.assertGet(reverse('parts-apply'), code=302)
        # member2 has no access
        response = self.assertPost(reverse('parts-apply'), member=self.member2, code=302)
        self.assertFalse(self.sub2.parts.first().active)
        # test activation
        self.assertPost(reverse('parts-apply'), {'parts[]': [self.sub2.parts.first().id]}, code=302)
        # check that sub is active
        self.assertTrue(self.sub2.parts.first().active)


    def testSubscriptionCancelled(self):
        self.sub.cancel()
        response = self.assertGet(reverse('manage-sub-pending'))
        # check that member list is correct
        objects = response.context['object_list']
        self.assertEqual(set(objects.order_by('id')), {self.sub, self.sub2})

    def testSubscriptionDeactivate(self):
        self.sub.cancel()
        self.assertGet(reverse('parts-apply'), code=302)
        self.assertTrue(self.sub.parts.first().active)
        # deactivate
        self.assertPost(reverse('parts-apply'), {'parts[]': [self.sub.parts.first().id]}, code=302)
        # check that sub is deactivated
        self.assertFalse(self.sub.parts.first().active)
