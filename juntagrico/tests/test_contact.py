from django.urls import reverse

from . import JuntagricoTestCase


class ContactTests(JuntagricoTestCase):

    def testContact(self):
        self.assertGet(reverse('contact'))

    def testContactPost(self):
        self.assertPost(reverse('contact'), {'subject': 'subject', 'copy': 'copy'})

    def testContactMember(self):
        self.assertGet(reverse('contact-member', args=[self.member.pk]), 404, self.member2)
        self.assertGet(reverse('contact-member', args=[self.area_admin.pk]))

    def testContactMemberPost(self):
        self.assertPost(reverse('contact-member', args=[self.member.pk]),
                        {'subject': 'subject', 'copy': 'copy'}, 404, self.member2)
        self.assertPost(reverse('contact-member', args=[self.area_admin.pk]),
                        {'subject': 'subject', 'copy': 'copy'})
