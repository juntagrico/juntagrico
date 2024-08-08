from django.dispatch import receiver
from django.test import override_settings
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

        self.assertPost(reverse('job', args=[self.job1.pk]), {'slots': 1, 'subscribe': True}, 302)
        self.assertEqual(self.job1.free_slots, 0)
        self.assertEqual(self.job1.assignment_set.first().amount, 1)
        self.assertTrue(self.signal_called)
        self.assertTrue(subscribed.disconnect(handler, sender=Job))

    def testJobExtras(self):
        self.assertPost(reverse('job', args=[self.job3.pk]), {'slots': 1, 'extra' + str(self.job_extra_type.id): str(self.job_extra_type.id), 'subscribe': True}, 302)
        self.assertEqual(self.job3.assignment_set.first().job_extras.count(), 1)
        self.assertGet(reverse('job', args=[self.job3.pk]))

    def testMultipleEntries(self):
        # should override slots not add
        self.assertPost(reverse('job', args=[self.job4.pk]), {'slots': 1, 'subscribe': True}, 302)
        self.assertEqual(self.job4.assignment_set.count(), 1)
        self.assertGet(reverse('job', args=[self.job4.pk]))
        self.assertPost(reverse('job', args=[self.job4.pk]), {'slots': 2, 'subscribe': True}, 302)
        self.assertEqual(self.job4.assignment_set.count(), 2)
        self.assertGet(reverse('job', args=[self.job4.pk]))
        self.assertPost(reverse('job', args=[self.job4.pk]), {'slots': 3, 'subscribe': True}, 302)
        self.assertEqual(self.job4.assignment_set.count(), 3)
        self.assertGet(reverse('job', args=[self.job4.pk]))

    def testInfiniteSlots(self):
        self.assertPost(reverse('job', args=[self.infinite_job.pk]), {'slots': 3, 'subscribe': True}, 302)
        self.assertEqual(self.infinite_job.assignment_set.count(), 3)
        self.assertGet(reverse('job', args=[self.infinite_job.pk]))

    def testOverassignement(self):
        self.assertPost(reverse('job', args=[self.job4.pk]), {'slots': 1000, 'subscribe': True})

    def testHours(self):
        with self.settings(ASSIGNMENT_UNIT='HOURS'):
            self.assertPost(reverse('job', args=[self.job5.pk]), {'slots': 1, 'subscribe': True}, 302)
            self.assertEqual(self.job5.assignment_set.first().amount, 2)

    def testUnsubscribe(self):
        # Unsubscribe should be prevented, because ALLOW_JOB_UNSUBSCRIBE=False
        # subscribe and try unsubscribing
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'subscribe': True}, 302)
        self.assertEqual(self.job6.occupied_slots, 1)
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'unsubscribe': True}, 200)
        self.assertEqual(self.job6.occupied_slots, 1)

        # subscribe for multiple slots and try unsubscribing from all
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 4, 'subscribe': True}, 302)
        self.assertEqual(self.job6.occupied_slots, 4)
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'unsubscribe': True}, 200)
        self.assertEqual(self.job6.occupied_slots, 4)


@override_settings(ALLOW_JOB_UNSUBSCRIBE=True)
class UnsubscribableJobTests(JobTests):
    def testUnsubscribe(self):
        # subscribe and unsubscribe job6
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'subscribe': True}, 302)
        self.assertEqual(self.job6.occupied_slots, 1)
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'unsubscribe': True}, 302)
        self.assertEqual(self.job6.occupied_slots, 0)

        # now we have no sign ups, so a repeated unsubscribe should return 200
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'unsubscribe': True})

        # subscribe for multiple slots and unsubscribe from all
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 4, 'subscribe': True}, 302)
        self.assertEqual(self.job6.occupied_slots, 4)
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'unsubscribe': True}, 302)
        self.assertEqual(self.job6.occupied_slots, 0)
