from django.urls import reverse

from . import JuntagricoTestCase


class ContactTests(JuntagricoTestCase):

    def testContact(self):
        self.assertGet(reverse('contact'))

    def testContactPost(self):
        self.assertPost(reverse('contact'), {'subject': 'subject', 'copy': 'copy'})
