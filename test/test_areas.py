from django.urls import reverse

from test.util.test import JuntagricoTestCase


class AreaTests(JuntagricoTestCase):

    def testAreas(self):
        self.assertGet(reverse('areas'))

    def testArea(self):
        self.assertGet(reverse('area', args=[self.area.pk]))

    def testAreaJoinAndLeave(self):
        self.assertGet(reverse('area-join', args=[self.area.pk]))
        self.assertEqual(self.area.members.count(), 1)
        self.assertGet(reverse('area-leave', args=[self.area.pk]))
        self.assertEqual(self.area.members.count(), 0)
