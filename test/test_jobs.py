from django.urls import reverse

from test.util.test import JuntagricoTestCase


class JobTests(JuntagricoTestCase):

    def testAssignments(self):
        self.assertSimpleGet(reverse('jobs'))

    def testAssignmentsAll(self):
        self.assertSimpleGet(reverse('jobs-all'))

    def testJob(self):
        self.assertSimpleGet(reverse('job', args=[self.job1.pk]))

    def testPastJob(self):
        self.assertSimpleGet(reverse('memberjobs'))

    def testParticipation(self):
        self.assertSimpleGet(reverse('areas'))

    def testTeam(self):
        self.assertSimpleGet(reverse('area', args=[self.area.pk]))

    def testAreaJoinAndLeave(self):
        self.assertSimpleGet(reverse('area-join', args=[self.area.pk]))
        self.assertEqual(self.area.members.count(), 1)
        self.assertSimpleGet(reverse('area-leave', args=[self.area.pk]))
        self.assertEqual(self.area.members.count(), 0)

    def testJobPost(self):
        self.client.force_login(self.member.user)
        response = self.client.post(reverse('job', args=[self.job1.pk]), {'jobs': 1})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.job1.free_slots(), 0)
