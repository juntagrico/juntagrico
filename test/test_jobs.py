from django.urls import reverse

from test.util.test import JuntagricoTestCase


class JobTests(JuntagricoTestCase):

    def testAssignments(self):
        self.assertGet(reverse('jobs'))

    def testAssignmentsAll(self):
        self.assertGet(reverse('jobs-all'))

    def testJob(self):
        self.assertGet(reverse('job', args=[self.job1.pk]))

    def testPastJob(self):
        self.assertGet(reverse('memberjobs'))

    def testParticipation(self):
        self.assertGet(reverse('areas'))

    def testTeam(self):
        self.assertGet(reverse('area', args=[self.area.pk]))

    def testAreaJoinAndLeave(self):
        self.assertGet(reverse('area-join', args=[self.area.pk]))
        self.assertEqual(self.area.members.count(), 1)
        self.assertGet(reverse('area-leave', args=[self.area.pk]))
        self.assertEqual(self.area.members.count(), 0)

    def testJobPost(self):
        self.client.force_login(self.member.user)
        self.assertPost(reverse('job', args=[self.job1.pk]), {'jobs': 1}, 302)
        self.assertEqual(self.job1.free_slots(), 0)
