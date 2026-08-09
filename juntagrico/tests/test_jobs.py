from django.core import mail
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from . import JuntagricoTestCase, JuntagricoJobTestCase
from ..entity.contact import MemberContact
from ..entity.jobs import Job, Assignment, OneTimeJob, JobType, RecuringJob, JobMessage
from ..entity.member import Member
from ..signals import subscribed, assignment_changed


class JobTests(JuntagricoTestCase):

    def testAssignments(self):
        self.assertGet(reverse('jobs'))

    def testAssignmentsAll(self):
        self.assertGet(reverse('jobs-all'))

    def testJob(self):
        job1_url = reverse('job', args=[self.job1.pk])
        self.assertGet(job1_url)
        self.assertGet(job1_url, member=self.area_admin)
        self.assertGet(job1_url, member=self.admin)
        self.assertGet(reverse('job', args=[self.one_time_job1.pk]))
        self.assertGet(reverse('job', args=[self.canceled_job.pk]))
        
    def testPastJob(self):
        self.assertGet(reverse('memberjobs'))
        self.assertGet(reverse('job', args=[self.past_job.pk]))

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

    def testJobCancel(self):
        # incomplete and unprivileged requests should fail
        self.assertGet(reverse('job-cancel'), 405)
        self.assertPost(reverse('job-cancel'), code=400)
        self.assertPost(reverse('job-cancel'), {'job_id': self.job1.id}, 403)
        self.job1.refresh_from_db()
        self.assertFalse(self.job1.canceled)
        # area admin who can edit jobs can cancel them
        self.assertPost(reverse('job-cancel'), {'job_id': self.job1.id}, 302, self.area_admin_job_modifier)
        self.job1.refresh_from_db()
        self.assertTrue(self.job1.canceled)
        # can save canceled job even when it has 0 slots
        self.job1.save()

    def testJobTimeChange(self):
        self.job2.time = timezone.now()
        self.job2.save()
        self.assertEqual(len(mail.outbox), 1)  # member notification

    def testJobByAccount(self):
        self.assertGet(reverse('job-by-account', args=[self.member.id]))
        self.assertGet(reverse('job-by-account', args=[self.member.id]), member=self.member2, code=403)
        self.assertGet(reverse('job-by-account', args=[self.member2.id]), member=self.member2)
        self.assertGet(reverse('job-by-account', args=[self.member.id]), member=self.admin)


class JobSignupAndNotificationTests(JuntagricoTestCase):
    def testJobSignup(self):
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
        self.assertEqual('Juntagrico - Neue Anmeldung zum Einsatz mit Mitteilung', mail.outbox[1].subject)
        self.assertTrue(subscribed.disconnect(handler, sender=Job))

    def _firstJobSignup(self, message=None):
        message = {'message': message} if message is not None else {}
        self.assertPost(reverse('job', args=[self.job1.pk]), {
            'slots': 1, 'subscribe': True
        } | message, 302, self.member2)
        self.assertEqual(mail.outbox[0].recipients(), [self.member2.email])

    @override_settings(ENABLE_NOTIFICATIONS=['job_subscribed'], FIRST_JOB_INFO=[])
    def testNotificationOnJobSignup(self):
        self._firstJobSignup()
        self.assertEqual(len(mail.outbox), 2)  # member and admin notification
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        self.assertEqual('Juntagrico - Neue Anmeldung zum Einsatz', mail.outbox[1].subject)

    @override_settings(FIRST_JOB_INFO=['overall', 'per_area', 'per_type'])
    def testFirstJobSignup(self):
        self._firstJobSignup()
        self.assertEqual(len(mail.outbox), 2)  # member and admin notification
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        self.assertEqual('Juntagrico - Erster Einsatz', mail.outbox[1].subject)

    @override_settings(FIRST_JOB_INFO=['overall', 'per_area', 'per_type'])
    def testFirstJobSignupWithMessage(self):
        self._firstJobSignup('hello')
        self.assertEqual(len(mail.outbox), 2)  # member and admin notification
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        self.assertEqual('Juntagrico - Erster Einsatz (mit Mitteilung)', mail.outbox[1].subject)

    @override_settings(FIRST_JOB_INFO=['per_area', 'per_type'])
    def testFirstJobInAreaSignup(self):
        self._firstJobSignup()
        self.assertEqual(len(mail.outbox), 2)  # member and admin notification
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        self.assertEqual('Juntagrico - Erster Einsatz im Tätigkeitsbereich "name"', mail.outbox[1].subject)

    @override_settings(FIRST_JOB_INFO=['per_area', 'per_type'])
    def testFirstJobInAreaSignupWithMessage(self):
        self._firstJobSignup('hello')
        self.assertEqual(len(mail.outbox), 2)  # member and admin notification
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        self.assertEqual('Juntagrico - Erster Einsatz im Tätigkeitsbereich "name" (mit Mitteilung)', mail.outbox[1].subject)

    @override_settings(FIRST_JOB_INFO=['per_type'])
    def testFirstJobInTypeSignup(self):
        self._firstJobSignup()
        self.assertEqual(len(mail.outbox), 2)  # member and admin notification
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        self.assertEqual('Juntagrico - Erster Einsatz in Job-Art "nameot"', mail.outbox[1].subject)

    @override_settings(FIRST_JOB_INFO=['per_type'])
    def testFirstJobInTypeSignupWithMessage(self):
        self._firstJobSignup('hello')
        self.assertEqual(len(mail.outbox), 2)  # member and admin notification
        self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        self.assertEqual('Juntagrico - Erster Einsatz in Job-Art "nameot" (mit Mitteilung)', mail.outbox[1].subject)

    @override_settings(FIRST_JOB_INFO=[])
    def testNoNotificationOnFirstJobSignup(self):
        self._firstJobSignup()
        self.assertEqual(len(mail.outbox), 1)  # only member notification


class JobConvertionTests(JuntagricoJobTestCase):
    def testConvertionToRecurringJob(self):
        self.assertPost(
            reverse('job-convert-to-recurring', args=[self.complex_one_time_job.id]),
            data={'submit': 'yes'},
            member=self.area_admin_job_modifier,
            code=302
        )
        # check that original job was removed
        self.assertFalse(OneTimeJob.objects.filter(pk=self.complex_one_time_job.pk).exists())
        # check if new job is complete
        new_type = JobType.objects.last()
        self.assertEqual(new_type.displayed_name, 'one_time_job')
        self.assertEqual(new_type.default_duration, 3)
        self.assertListEqual(sorted(new_type.get_emails()), [self.member3.email, 'test@test.org'])
        new_job = RecuringJob.objects.last()
        self.assertEqual(new_job.slots, 1)
        self.assertEqual(new_job.additional_description, '')
        self.assertEqual(new_job.duration_override, None)
        self.assertListEqual(sorted(new_job.get_emails()), [self.member3.email, 'test@test.org'])
        self.assertSetEqual(new_job.participant_emails, {self.member.email})

    def testConvertionToRecurringJobUsingExistingButNotCoordinatedJobType(self):
        # area admin can't convert to job type of area2
        response = self.assertPost(
            reverse('job-convert-to-recurring', args=[self.complex_one_time_job.id]),
            data={'job_type': self.job_type2.pk, 'submit': 'yes'},
            member=self.area_admin_job_modifier,
            code=302
        )
        # check redirect and no changes
        self.assertRedirects(response, reverse('job', args=[self.complex_one_time_job.pk]), 302)
        self.assertTrue(OneTimeJob.objects.filter(pk=self.complex_one_time_job.pk).exists())

    def testConvertionToRecurringJobUsingExistingJobType(self):
        response = self.assertPost(
            reverse('job-convert-to-recurring', args=[self.complex_one_time_job.id]),
            data={'job_type': self.job_type.pk, 'submit': 'yes'},
            member=self.area_admin_job_modifier,
            code=302
        )
        # check success and redirect
        new_job = RecuringJob.objects.last()
        self.assertRedirects(response, reverse('job', args=[new_job.pk]), 302)
        # check that original job was removed
        self.assertFalse(OneTimeJob.objects.filter(pk=self.complex_one_time_job.pk).exists())
        # check that existing type is unchanged
        new_type = new_job.type
        self.assertEqual(new_type.name, 'nameot')
        self.assertEqual(new_type.default_duration, 2)
        self.assertListEqual(sorted(new_type.get_emails()), ['email_contact@example.org'])
        # check if new job is complete
        self.assertEqual(new_job.slots, 1)
        self.assertEqual(new_job.additional_description, '')
        self.assertEqual(new_job.duration_override, 3)
        self.assertListEqual(sorted(new_job.get_emails()), [self.member3.email, 'test@test.org'])
        self.assertSetEqual(new_job.participant_emails, {self.member.email})

    def testConvertionToRecurringJobOfNotCoordinatedArea(self):
        # fails
        self.complex_one_time_job.activityarea = self.area2
        self.complex_one_time_job.save()
        self.assertPost(
            reverse('job-convert-to-recurring', args=[self.complex_one_time_job.id]),
            data={'submit': 'yes'},
            member=self.area_admin_job_modifier,
            code=403
        )

    def testConvertionToOneTimeJobsOfNotCoordinatedArea(self):
        # fails
        self.assertPost(
            reverse('job-convert-to-one-time'),
            data={'job_id': self.complex_job.pk},
            member=self.area_admin_job_modifier,
            code=403
        )

    def testConvertionToOneTimeJobsOfCoordinatedArea(self):
        self.complex_job_type.activityarea = self.area
        self.complex_job_type.save()
        self.assertPost(
            reverse('job-convert-to-one-time'),
            data={'job_id': self.complex_job.pk},
            member=self.area_admin_job_modifier,
            code=302
        )
        # check that original job was removed
        self.assertFalse(RecuringJob.objects.filter(pk=self.complex_job.pk).exists())
        # check if new job is complete
        new_job = OneTimeJob.objects.last()
        self.assertEqual(new_job.displayed_name, 'complex_job_type_name')
        self.assertEqual(new_job.default_duration, 6)  # override from job
        self.assertEqual(new_job.activityarea, self.area)
        self.assertEqual(new_job.slots, 1)
        self.assertEqual(new_job.description, 'complex_job_type_description\nExtra Description')
        self.assertListEqual(sorted(new_job.get_emails()), [self.member2.email, 'test@test.org'])
        self.assertSetEqual(new_job.participant_emails, {self.member2.email})


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
        self.assertEqual(mail.outbox[1].subject, 'Juntagrico - Abmeldung vom Einsatz')
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
        self.assertPost(
            reverse('assignment-add', args=[self.job2.pk]),
            {'account': self.member3.pk, 'slots': 1},
            403,
            self.member2,
        )

    def testAssignmentAdd(self, admin=None, participant=None):
        admin = admin or self.member  # has general permission to change assignments
        participant = participant or self.member3
        self.signal_called = False

        @receiver(assignment_changed, sender=Member)
        def handler(instance, job, count, *args, **kwargs):
            self.signal_called = True
            self.assertEqual(count, 1)
            self.assertEqual(job, self.job2)
            self.assertEqual(instance.pk, participant.pk)

        self.assertGet(reverse('job', args=[self.job2.pk]), member=admin)
        # test add participant
        self.assertPost(reverse('assignment-add', args=[self.job2.pk]),
                        {'add-account': participant.pk, 'add-slots': 1}, 302, admin)
        self.assertEqual(self.job2.occupied_slots, 2)
        self.assertSetEqual(self.job2.participant_emails, {self.member.email, participant.email})
        self.assertTrue(self.signal_called)
        self.assertEqual(len(mail.outbox), 2 if admin != participant else 1)  # (member notification +) admin notification
        if admin != participant:
            # if member edits their own assignment, no notification is sent to them
            self.assertEqual(mail.outbox[0].recipients(), [participant.email])
        self.assertEqual(mail.outbox[-1].recipients(), ['email_contact@example.org'])
        self.assertIn(participant.email, mail.outbox[-1].body, 'Admin notification must contain members email address')
        mail.outbox.clear()
        self.assertTrue(assignment_changed.disconnect(handler, sender=Member))

    def testAssignmentAddBySelf(self):
        self.testAssignmentAdd(self.area_admin, self.area_admin)

    def testAssignmentAddByCoordinator(self):
        self.testAssignmentAdd(self.area_admin)

    def testAssignmentAddByAssignmentModifier(self):
        self.testAssignmentAdd(self.area_admin_assignment_modifier)

    def testAssignmentEdit(self, admin=None, admin_notification=True):
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
        # (member notification +) admin notification
        self.assertEqual(len(mail.outbox), admin_notification + (admin != self.member))
        if admin != self.member:
            # if member edits their own assignment, no notification is sent to them
            self.assertEqual(mail.outbox[0].recipients(), [self.member.email])
        if admin_notification:
            self.assertEqual(mail.outbox[-1].recipients(), ['email_contact@example.org'])
            self.assertIn(self.member.email, mail.outbox[-1].body, 'Admin notification must contain members email address')
        mail.outbox.clear()
        self.assertTrue(assignment_changed.disconnect(handler, sender=Member))

    def testAssignmentNotDelete(self):
        # member does not have permission to delete
        self.assertPost(reverse('assignment-edit', args=[self.job2.pk, self.member.pk]),
                        {'edit-slots': 0}, 302, self.member)
        # test that slots are unchanged
        self.assertEqual(self.job2.occupied_slots, 1)

    def testAssignmentDelete(self, admin=None, admin_notification=True):
        admin = admin or self.admin
        self.assertPost(reverse('assignment-edit', args=[self.job2.pk, self.member.pk]),
                        {'edit-slots': 0}, 302, admin)
        self.assertEqual(self.job2.occupied_slots, 0)
        self.assertEqual(len(mail.outbox), 1 + admin_notification)  # member notification and coordinator notification
        self.assertEqual(mail.outbox[0].recipients(), [self.member.email])
        if admin_notification:
            self.assertEqual(mail.outbox[1].recipients(), ['email_contact@example.org'])
        mail.outbox.clear()

    def testAssignmentEditByCoordinator(self):
        self.testAssignmentEdit(self.area_admin)
        self.testAssignmentDelete(self.area_admin)
        self.testAssignmentEdit(self.area_admin_assignment_modifier)
        self.testAssignmentDelete(self.area_admin_assignment_modifier)

    def testAssignmentEditBySoleCoordinator(self):
        self.job2.contact_set.add(MemberContact(member=self.area_admin), bulk=False)
        # only member is notified as editor is sole coordinator
        self.testAssignmentEdit(self.area_admin, False)
        self.testAssignmentDelete(self.area_admin, False)


class JobValidationTests(JuntagricoTestCase):
    """
    Test validation rules for jobs
    """
    def testOneTimeJobWithZeroSlotsAndNoInfiniteSlots(self):
        """Test that OneTimeJob with slots=0 and infinite_slots=False raises ValidationError"""
        job = OneTimeJob(
            name='Invalid Job',
            description='Test job with zero slots and no infinite slots',
            activityarea=self.area,
            default_duration=2,
            slots=0,
            infinite_slots=False,
            time=self.job1.time,
            location=self.job_type.location
        )
        with self.assertRaises(ValidationError) as cm:
            job.full_clean()
        self.assertIn('Ein Job muss entweder mehr als 0 Plätze haben oder "Unendlich Plätze" aktiviert haben', str(cm.exception))

    def testOneTimeJobWithZeroSlotsButInfiniteSlots(self):
        """Test that OneTimeJob with slots=0 but infinite_slots=True is valid"""
        job = OneTimeJob(
            name='Valid Infinite Job',
            description='Test job with infinite slots',
            activityarea=self.area,
            default_duration=2,
            slots=0,
            infinite_slots=True,
            time=self.job1.time,
            location=self.job_type.location
        )
        # Should not raise ValidationError
        job.full_clean()
        job.save()
        self.assertEqual(job.slots, 0)
        self.assertTrue(job.infinite_slots)

    def testOneTimeJobWithPositiveSlots(self):
        """Test that OneTimeJob with slots > 0 is valid"""
        job = OneTimeJob(
            name='Valid Job',
            description='Test job with positive slots',
            activityarea=self.area,
            default_duration=2,
            slots=5,
            infinite_slots=False,
            time=self.job1.time,
            location=self.job_type.location
        )
        # Should not raise ValidationError
        job.full_clean()
        job.save()
        self.assertEqual(job.slots, 5)
        self.assertFalse(job.infinite_slots)

    def testRecuringJobWithZeroSlotsAndNoInfiniteSlots(self):
        """Test that RecuringJob with slots=0 and infinite_slots=False raises ValidationError"""
        job = RecuringJob(
            slots=0,
            infinite_slots=False,
            time=self.job1.time,
            type=self.job_type
        )
        with self.assertRaises(ValidationError) as cm:
            job.full_clean()
        self.assertIn('Ein Job muss entweder mehr als 0 Plätze haben oder "Unendlich Plätze" aktiviert haben', str(cm.exception))

    def testRecuringJobWithZeroSlotsButInfiniteSlots(self):
        """Test that RecuringJob with slots=0 but infinite_slots=True is valid"""
        job = RecuringJob(
            slots=0,
            infinite_slots=True,
            time=self.job1.time,
            type=self.job_type
        )
        # Should not raise ValidationError
        job.full_clean()
        job.save()
        self.assertEqual(job.slots, 0)
        self.assertTrue(job.infinite_slots)


class JobMessageTests(JuntagricoTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.job_message = JobMessage.objects.create(
            job=cls.job2,
            account=cls.member,
            message='Test message',
        )
        JobMessage.objects.create(
            job=cls.past_job,
            account=cls.member2,
            message='old message',
        )

    def testJobMessage(self):
        job2_url = reverse('job', args=[self.job2.pk])
        self.assertGet(job2_url)
        self.assertGet(job2_url, member=self.area_admin)
        self.assertGet(job2_url, member=self.admin)

    def testAddJobMessage(self):
        data = {
            'message': 'new message',
        }
        # non-participant can't message
        self.assertPost(
            reverse('job-message-add', args=[self.job2.pk]), data, 403, member=self.member2
        )
        # participant can message
        self.assertPost(reverse('job-message-add', args=[self.job2.pk]), data, 302, member=self.member)
        self.assertEqual(self.job2.messages.count(), 2)

    def testDeleteJobMessage(self):
        # can't delete others messages
        self.assertPost(reverse('job-message-remove', args=[self.job_message.pk]), code=302, member=self.member2)
        self.assertEqual(self.job2.messages.count(), 1)
        # can delete own messages
        self.assertPost(reverse('job-message-remove', args=[self.job_message.pk]), code=302, member=self.member)
        self.assertEqual(self.job2.messages.count(), 0)

    def testAdminDeleteJobMessage(self):
        # area admin can delete messages
        self.assertPost(reverse('job-message-remove', args=[self.job_message.pk]), code=302, member=self.area_admin)
        self.assertEqual(self.job2.messages.count(), 0)

    def testJobMessagesPurge(self):
        JobMessage.KEEP_HOURS = 1
        self.assertEqual(self.past_job.messages.count(), 1)
        self.assertGet(reverse('job', args=[self.past_job.pk]), member=self.area_admin)
        self.assertEqual(self.past_job.messages.count(), 0)
