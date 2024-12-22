from django.core import mail
from django.urls import reverse

from . import JuntagricoTestCase


class AreaTests(JuntagricoTestCase):

    def testAreas(self):
        self.assertGet(reverse('areas'))

    def testArea(self):
        self.assertGet(reverse('area', args=[self.area.pk]))

    def testAreaJoinAndLeave(self):
        self.assertGet(reverse('area-join', args=[self.area.pk]))
        self.assertEqual(self.area.members.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['email_contact@example.org'])
        mail.outbox = []

        self.assertGet(reverse('area-leave', args=[self.area.pk]))
        self.assertEqual(self.area.members.count(), 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['email_contact@example.org'])
