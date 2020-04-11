from django.urls import reverse
from django.utils import timezone

from test.util.test import JuntagricoTestCase


class ProfileTests(JuntagricoTestCase):

    def testProfile(self):
        self.assertGet(reverse('profile'))

    def testProfilePost(self):
        self.assertPost(reverse('profile'), {'iban': 'iban'})

    def testCancelMembership(self):
        self.assertGet(reverse('cancel-membership'))

    def testCancelMembershipPost(self):
        self.assertPost(reverse('cancel-membership'), code=302)

    def testDeactivateMembership(self):
        # must first cancel and pay back the shares
        for share in self.member.active_shares:
            share.cancelled_date = timezone.now().date()
            share.termination_date = timezone.now().date()
            share.payback_date = timezone.now().date()
            share.save()
        # and delete the subscription
        self.member.subscription.delete()
        self.assertPost(reverse('member-deactivate', args=(self.member.pk,)), code=302)
        self.member.refresh_from_db()
        self.assertTrue(self.member.inactive)
