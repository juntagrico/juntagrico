from django.dispatch import receiver
from django.urls import reverse

from . import JuntagricoTestCase
from ..entity.jobs import Job
from ..signals import subscribed


class JobTests(JuntagricoTestCase):

    def testAssignments(self):
        self.assertGet(reverse('jobs'))

    def testAssignmentsAll(self):
        self.assertGet(reverse('jobs-all'))

    def testJob(self):
        self.assertGet(reverse('job', args=[self.job1.pk]))
        self.assertGet(reverse('job', args=[self.one_time_job1.pk]))

    def testPastJob(self):
        self.assertGet(reverse('memberjobs'))

    def testJobPost(self):
        self.signal_called = False

        @receiver(subscribed, sender=Job)
        def handler(instance, member, count, *args, **kwargs):
            self.signal_called = True
            self.assertEqual(count, 1)
            self.assertEqual(instance.pk, self.job1.pk)
            self.assertEqual(member, self.member)

        self.assertPost(reverse('job', args=[self.job1.pk]), {'jobs': 1}, 302)
        self.assertEqual(self.job1.free_slots, 0)
        self.assertEqual(self.job1.assignment_set.first().amount, 1)
        self.assertTrue(self.signal_called)
        self.assertTrue(subscribed.disconnect(handler, sender=Job))

    def testJobExtras(self):
        self.assertPost(reverse('job', args=[self.job3.pk]), {'jobs': 1, 'extra' + str(self.job_extra_type.id): str(self.job_extra_type.id)}, 302)
        self.assertEqual(self.job3.assignment_set.first().job_extras.count(), 1)
        self.assertGet(reverse('job', args=[self.job3.pk]))

    def testMultipleEntries(self):
        self.assertPost(reverse('job', args=[self.job4.pk]), {'jobs': 1}, 302)
        self.assertEqual(self.job4.assignment_set.count(), 1)
        self.assertGet(reverse('job', args=[self.job4.pk]))
        self.assertPost(reverse('job', args=[self.job4.pk]), {'jobs': 1}, 302)
        self.assertEqual(self.job4.assignment_set.count(), 2)
        self.assertGet(reverse('job', args=[self.job4.pk]))
        self.assertPost(reverse('job', args=[self.job4.pk]), {'jobs': 3}, 302)
        self.assertEqual(self.job4.assignment_set.count(), 5)
        self.assertGet(reverse('job', args=[self.job4.pk]))

    def testInfiniteSlots(self):
        self.assertPost(reverse('job', args=[self.infinite_job.pk]), {'jobs': 3}, 302)
        self.assertEqual(self.infinite_job.assignment_set.count(), 3)
        self.assertGet(reverse('job', args=[self.infinite_job.pk]))

    def testOverassignement(self):
        self.assertPost(reverse('job', args=[self.job4.pk]), {'jobs': 1000})

    def testHours(self):
        with self.settings(ASSIGNMENT_UNIT='HOURS'):
            self.assertPost(reverse('job', args=[self.job5.pk]), {'jobs': 1}, 302)
            self.assertEqual(self.job5.assignment_set.first().amount, 2)
