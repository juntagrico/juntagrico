from django.urls import reverse

from test.util.test import JuntagricoTestCase


class ContactTests(JuntagricoTestCase):

    def testContact(self):
        self.assertGet(reverse('contact'))

    def testContactPost(self):
        self.assertPost(reverse('contact'), {'subject': 'subject', 'copy': 'copy'})

    def testContactMember(self):
        self.assertGet(reverse('contact-member', args=[self.member.pk]), code=404)
        self.assertGet(reverse('contact-member', args=[self.area_admin.pk]))

    def testContactMemberPost(self):
        self.assertPost(reverse('contact-member', args=[self.member.pk]), {'subject': 'subject', 'copy': 'copy'}, code=404)
        self.assertPost(reverse('contact-member', args=[self.area_admin.pk]), {'subject': 'subject', 'copy': 'copy'})
