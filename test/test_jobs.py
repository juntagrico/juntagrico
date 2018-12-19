from django.test import TestCase

from test.util.test_data import create_test_data


class HomeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def testAssignments(self):
        self.client.force_login(self.member.user)
        response = self.client.get('/my/assignments')
        print(response)
        self.assertEqual(response.status_code, 200)

    def testAssignmentsAll(self):
        self.client.force_login(self.member.user)
        response = self.client.get('/my/assignments/all')
        self.assertEqual(response.status_code, 200)

    def testJob(self):
        self.client.force_login(self.member.user)
        response = self.client.get('/my/jobs/' + str(self.job1.pk) + '/')
        self.assertEqual(response.status_code, 200)

    def testPastJob(self):
        self.client.force_login(self.member.user)
        response = self.client.get('/my/pastjobs')
        self.assertEqual(response.status_code, 200)

    def testParticipation(self):
        self.client.force_login(self.member.user)
        response = self.client.get('/my/participation')
        self.assertEqual(response.status_code, 200)

    def testTeam(self):
        self.client.force_login(self.member.user)
        response = self.client.get('/my/teams/'+str(self.area.pk)+'/')
        self.assertEqual(response.status_code, 200)

    def testParticipationPost(self):
        self.client.force_login(self.member.user)
        response = self.client.post('/my/participation', {'area'+str(self.area.pk): 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.area.members.count(), 1)

    def testJobPost(self):
        self.client.force_login(self.member.user)
        response = self.client.post('/my/jobs/' + str(self.job1.pk) + '/', {'jobs': 1})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.job1.free_slots(), 0)
