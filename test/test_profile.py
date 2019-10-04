from django.urls import reverse

from test.util.test import JuntagricoTestCase


class ProfileTests(JuntagricoTestCase):

    def testProfile(self):
        self.assertGet(reverse('profile'))

    def testProfilePost(self):
        self.assertPost(reverse('profile'), {'iban': 'iban'})

    def testCancelMembership(self):
        self.assertGet(reverse('cancel-membership'))

    def testCancelMembershipPost(self):
        self.assertPost(reverse('cancel-membership'), data={'end_date':'9999-01-01'}, code=302)
