from django.core import mail
from django.dispatch import receiver
from django.test import override_settings
from django.urls import reverse

from . import JuntagricoTestCase
from ..entity.jobs import Job, Assignment
from ..entity.member import Member
from ..signals import subscribed, assignment_changed


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

        self.assertPost(reverse('job', args=[self.job1.pk]), {'slots': 1, 'subscribe': True, 'message': 'hello'}, 302)
        self.assertEqual(self.job1.free_slots, 0)
        self.assertEqual(self.job1.assignment_set.first().amount, 1)
        self.assertTrue(self.signal_called)
        self.assertEqual(len(mail.outbox), 2)  # member and admin notification
        self.assertEqual(mail.outbox[0].recipients(), [self.member.email])
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        self.assertTrue(subscribed.disconnect(handler, sender=Job))

    def testJobExtras(self):
        self.assertPost(reverse('job', args=[self.job3.pk]), {'slots': 1, 'extra' + str(self.job_extra_type.id): str(self.job_extra_type.id), 'subscribe': True}, 302)
        self.assertEqual(self.job3.assignment_set.first().job_extras.count(), 1)
        self.assertGet(reverse('job', args=[self.job3.pk]))

    def testMultipleEntries(self):
        # should override slots not add
        self.assertPost(reverse('job', args=[self.job4.pk]), {'slots': 1, 'subscribe': True}, 302)
        self.assertEqual(self.job4.assignment_set.count(), 1)
        self.assertEqual(len(mail.outbox), 1)  # member notification, no admin notification, because of no message
        mail.outbox = []
        self.assertGet(reverse('job', args=[self.job4.pk]))
        self.assertPost(reverse('job', args=[self.job4.pk]), {'slots': 2, 'subscribe': True}, 302)
        self.assertEqual(self.job4.assignment_set.count(), 2)
        self.assertEqual(len(mail.outbox), 2)  # member and admin notification
        self.assertEqual(mail.outbox[0].recipients(), [self.member.email])
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        mail.outbox = []
        self.assertGet(reverse('job', args=[self.job4.pk]))
        self.assertPost(reverse('job', args=[self.job4.pk]), {'slots': 3, 'subscribe': True}, 302)
        self.assertEqual(self.job4.assignment_set.count(), 3)
        self.assertGet(reverse('job', args=[self.job4.pk]))
        self.assertEqual(len(mail.outbox), 2)  # member and admin notification
        self.assertEqual(mail.outbox[0].recipients(), [self.member.email])
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        mail.outbox = []

    def testInfiniteSlots(self):
        self.assertPost(reverse('job', args=[self.infinite_job.pk]), {'slots': 3, 'subscribe': True}, 302)
        self.assertEqual(self.infinite_job.assignment_set.count(), 3)
        self.assertGet(reverse('job', args=[self.infinite_job.pk]))

    def testOverassignement(self):
        assignment = Assignment.objects.create(job=self.job4, member=self.member, amount=2)
        self.assertPost(reverse('job', args=[self.job4.pk]), {'slots': 1000, 'subscribe': True})
        # ensure that assignment is not modified
        self.assertEqual(self.job4.assignment_set.count(), 1)
        assignment.refresh_from_db()
        self.assertEqual(assignment.amount, 2)
        # assert nobody was notified
        self.assertEqual(len(mail.outbox), 0)

    def testHours(self):
        with self.settings(ASSIGNMENT_UNIT='HOURS'):
            self.assertPost(reverse('job', args=[self.job5.pk]), {'slots': 1, 'subscribe': True}, 302)
            self.assertEqual(self.job5.assignment_set.first().amount, 2)

    def testUnsubscribe(self):
        # Unsubscribe should be prevented, because ALLOW_JOB_UNSUBSCRIBE=False
        # subscribe and try unsubscribing
        Assignment.objects.create(job=self.job6, member=self.member, amount=1)
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'unsubscribe': True}, 200)
        self.assertEqual(self.job6.occupied_slots, 1)

        # subscribe for multiple slots and try unsubscribing from all
        Assignment.objects.create(job=self.job6, member=self.member, amount=1)
        Assignment.objects.create(job=self.job6, member=self.member, amount=1)
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'unsubscribe': True}, 200)
        self.assertEqual(self.job6.occupied_slots, 3)
        # assert nobody was notified
        self.assertEqual(len(mail.outbox), 0)


@override_settings(ALLOW_JOB_UNSUBSCRIBE=True)
class UnsubscribableJobTests(JobTests):
    def testUnsubscribe(self):
        # subscribe and unsubscribe job6
        Assignment.objects.create(job=self.job6, member=self.member, amount=1)
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'unsubscribe': True}, 302)
        self.assertEqual(self.job6.occupied_slots, 0)
        # assert member and admin notification
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].recipients(), [self.member.email])
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        mail.outbox = []

        # now we have no sign ups, so a repeated unsubscribe should return 200
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'unsubscribe': True})

        # unsubscribe from multiple slots
        Assignment.objects.create(job=self.job6, member=self.member, amount=1)
        Assignment.objects.create(job=self.job6, member=self.member, amount=1)
        self.assertPost(reverse('job', args=[self.job6.pk]), {'slots': 1, 'unsubscribe': True}, 302)
        self.assertEqual(self.job6.occupied_slots, 0)
        # assert member and admin notification
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].recipients(), [self.member.email])
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])


class AssignmentTests(JuntagricoTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.job2.slots = 2
        cls.job2.save()

    def testPermission(self):
        self.assertGet(reverse('assignment-edit', args=[self.job2.pk, self.member.pk]), 403, self.member2)
        self.assertPost(reverse('assignment-edit', args=[self.job2.pk, self.member.pk]), {'slots': 2},
                        403, self.member2)
        self.assertEqual(self.job2.occupied_slots, 1)

    def testAssignmentEdit(self, admin=None):
        admin = admin or self.member  # has general permission to change assignments
        self.signal_called = False

        @receiver(assignment_changed, sender=Member)
        def handler(instance, job, count, *args, **kwargs):
            self.signal_called = True
            self.assertEqual(count, 2)
            self.assertEqual(job, self.job2)
            self.assertEqual(instance.pk, self.member.pk)

        self.assertGet(reverse('assignment-edit', args=[self.job2.pk, self.member.pk]), member=admin)
        # test increase subscription
        self.assertPost(reverse('assignment-edit', args=[self.job2.pk, self.member.pk]),
                        {'edit-slots': 2}, 302, admin)
        self.assertEqual(self.job2.occupied_slots, 2)
        self.assertTrue(self.signal_called)
        self.assertEqual(len(mail.outbox), 2 if admin != self.member else 1)  # (member notification +) admin notification
        if admin != self.member:
            # if member edits their own assignment, no notification is sent to them
            self.assertEqual(mail.outbox[0].recipients(), [self.member.email])
        self.assertEqual(mail.outbox[-1].recipients(), ['email_contact@example.org'])
        mail.outbox.clear()
        self.assertTrue(assignment_changed.disconnect(handler, sender=Member))

    def testAssignmentNotDelete(self):
        # member does not have permission to delete
        self.assertPost(reverse('assignment-edit', args=[self.job2.pk, self.member.pk]),
                        {'edit-slots': 0}, 302, self.member)
        # test that slots are unchanged
        self.assertEqual(self.job2.occupied_slots, 1)

    def testAssignmentDelete(self, admin=None):
        admin = admin or self.admin
        self.assertPost(reverse('assignment-edit', args=[self.job2.pk, self.member.pk]),
                        {'edit-slots': 0}, 302, admin)
        self.assertEqual(self.job2.occupied_slots, 0)
        self.assertEqual(len(mail.outbox), 2)  # member notification and coordinator notification
        self.assertEqual(mail.outbox[0].recipients(), [self.member.email])
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])

    def testAssignmentEditByCoordinator(self):
        self.testAssignmentEdit(self.area_admin)
        self.testAssignmentDelete(self.area_admin)
