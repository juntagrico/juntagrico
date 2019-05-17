from test.util.test import JuntagricoTestCase


class JobTests(JuntagricoTestCase):

    def testAssignments(self):
        self.assertSimpleGet('/my/assignments')

    def testAssignmentsAll(self):
        self.assertSimpleGet('/my/assignments/all')

    def testJob(self):
        self.assertSimpleGet('/my/jobs/' + str(self.job1.pk) + '/')

    def testPastJob(self):
        self.assertSimpleGet('/my/pastjobs')

    def testParticipation(self):
        self.assertSimpleGet('/my/participation')

    def testTeam(self):
        self.assertSimpleGet('/my/area/' + str(self.area.pk) + '/')

    def testAreaJoinAndLeave(self):
        self.assertSimpleGet('/my/area/' + str(self.area.pk) + '/join')
        self.assertEqual(self.area.members.count(), 1)
        self.assertSimpleGet('/my/area/' + str(self.area.pk) + '/leave')
        self.assertEqual(self.area.members.count(), 0)

    def testJobPost(self):
        self.client.force_login(self.member.user)
        response = self.client.post('/my/jobs/' + str(self.job1.pk) + '/', {'jobs': 1})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.job1.free_slots(), 0)
