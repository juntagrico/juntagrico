from django.core import mail
from django.urls import reverse

from . import JuntagricoTestCase


class AreaTests(JuntagricoTestCase):

    def testAreas(self):
        self.assertGet(reverse('areas'))

    def testArea(self):
        self.assertGet(reverse('area', args=[self.area.pk]))

    def testAreaJoinAndLeave(self):
        self.assertGet(reverse('area-join', args=[self.area2.pk]))
        self.assertEqual(self.area2.members.count(), 1)
        self.assertEqual(len(mail.outbox), 2)  # one per area admin
        recipients = sorted(mail.outbox[0].recipients() + mail.outbox[1].recipients())
        self.assertEqual(recipients, ['areaadmin@email.org', 'email2@email.org'])
        mail.outbox = []

        self.assertGet(reverse('area-leave', args=[self.area2.pk]))
        self.assertEqual(self.area2.members.count(), 0)
        self.assertEqual(len(mail.outbox), 2)  # one per area admin
        recipients = sorted(mail.outbox[0].recipients() + mail.outbox[1].recipients())
        self.assertEqual(recipients, ['areaadmin@email.org', 'email2@email.org'])
