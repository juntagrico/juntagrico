import datetime

from django.core.exceptions import ValidationError
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from juntagrico.admins.forms.delivery_copy_form import DeliveryCopyForm
from juntagrico.admins.forms.job_copy_form import JobMassCopyForm, JobMassCopyToFutureForm
from juntagrico.admins.forms.location_replace_form import LocationReplaceForm
from juntagrico.entity.delivery import Delivery
from juntagrico.entity.jobs import RecuringJob, OneTimeJob, JobType
from juntagrico.entity.location import Location
from . import JuntagricoTestCase, JuntagricoJobTestCase
from ..entity.contact import EmailContact, MemberContact


class AreaAdminTestMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_member = cls.area_admin_job_modifier
        cls.new_area = cls.area  # can't change it to other area
        cls.new_date = str(datetime.date.today() + datetime.timedelta(days=1))  # must be in the future
        cls.new_contact = cls.area.coordinators.first()  # must be an area coordinator


class JobCopyTestCase(JuntagricoTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        time = timezone.now() + timezone.timedelta(hours=2)
        cls.complex_job_data = {
            'slots': 1,
            'time': time,
            'type': cls.job_type,
            'infinite_slots': True,
            'multiplier': 2,
            'additional_description': 'Extra Description',
            'duration_override': 6
        }
        cls.complex_job = RecuringJob.objects.create(**cls.complex_job_data)
        cls.email_contact = EmailContact(email='test@test.org')
        cls.member_contact = MemberContact(member=cls.member2, display=MemberContact.DISPLAY_EMAIL)
        cls.complex_job.contact_set.add(cls.email_contact, bulk=False)
        cls.complex_job.contact_set.add(cls.member_contact, bulk=False)

        cls.default_member = cls.admin
        cls.new_date = '2025-12-10'
        cls.new_contact = cls.member


class JobCopyFormTests(JobCopyTestCase):
    def testMassCopyJobForm(self):
        # test 0 copies (fails)
        initial_count = RecuringJob.objects.all().count()
        data = {'type': self.job1.type.pk,
                'new_time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '26.07.2020',
                'end_date': '26.07.2020',
                'weekly': '7'
                }
        form = JobMassCopyForm(instance=self.job1, data=data)
        form.full_clean()
        with self.assertRaises(ValidationError):
            # should raise, because no jobs are created in this date range
            form.clean()

        # test 1 copy
        self.complex_job.time = datetime.datetime.now()
        data = {'type': self.complex_job.type.pk,
                'new_time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '01.07.2020',
                'end_date': '07.07.2020',
                'weekly': '7'
                }
        form = JobMassCopyForm(instance=self.complex_job, data=data)
        form.full_clean()
        form.clean()
        form.save()
        self.assertEqual(RecuringJob.objects.all().count(), initial_count + 1)
        # check completeness of copy
        new_job = RecuringJob.objects.last()
        self.assertEqual(self.complex_job.type, new_job.type)
        self.assertEqual(self.complex_job.slots, new_job.slots)
        self.assertEqual(self.complex_job.infinite_slots, new_job.infinite_slots)
        dt = datetime.datetime.fromisoformat('2020-07-06T' + data['new_time'])
        if settings.USE_TZ:
            dt = dt.astimezone(timezone.get_default_timezone())
        self.assertEqual(dt, new_job.time)
        self.assertEqual(self.complex_job.multiplier, new_job.multiplier)
        self.assertEqual(self.complex_job.additional_description, new_job.additional_description)
        self.assertEqual(self.complex_job.duration_override, new_job.duration_override)
        # Test 2 copies
        data = {'type': self.job1.type.pk,
                'new_time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '01.07.2020',
                'end_date': '15.07.2020',
                'weekly': '14'
                }
        form = JobMassCopyForm(instance=self.job1, data=data)
        form.full_clean()
        form.save()
        self.assertEqual(RecuringJob.objects.all().count(), initial_count + 2)

    def testMassCopyJobToFutureForm(self):
        # test failing case
        initial_count = RecuringJob.objects.all().count()
        data = {'type': self.job1.type.pk,
                'new_time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '01.07.2020',
                'end_date': '07.07.2020',
                'weekly': '7'
                }
        form = JobMassCopyToFutureForm(instance=self.job1, data=data)
        form.full_clean()
        with self.assertRaises(ValidationError) as validation_error:
            # should raise, because jobs are in the past
            form.clean()
        self.assertEqual(validation_error.exception.code, 'date_in_past')

        today = datetime.date.today()
        # test successful case
        data = {'type': self.job1.type.pk,
                'new_time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': today + datetime.timedelta(1),
                'end_date': today + datetime.timedelta(7),
                'weekly': '7'
                }
        form = JobMassCopyToFutureForm(instance=self.job1, data=data)
        form.full_clean()
        form.clean()
        form.save()
        self.assertEqual(RecuringJob.objects.all().count(), initial_count + 1)


class JobCopyTests(JobCopyTestCase):
    def testCopyJob(self):
        self.assertGet(reverse('admin:action-copy-job', args=(self.complex_job.pk,)))
        # test job copy changing entries
        data = {
            "type": str(self.complex_job.type.pk),
            "slots": "2",
            "multiplier": "3.0",
            "additional_description": "New Description",
            "duration_override": "9",
            'time_0': self.new_date, 'time_1': "13:46:46",
            "juntagrico-contact-content_type-object_id-TOTAL_FORMS": "3",
            "juntagrico-contact-content_type-object_id-INITIAL_FORMS": "2",
            "juntagrico-contact-content_type-object_id-MIN_NUM_FORMS": "0",
            "juntagrico-contact-content_type-object_id-MAX_NUM_FORMS": "1000",
            "juntagrico-contact-content_type-object_id-0-DELETE": "on",
            "juntagrico-contact-content_type-object_id-0-email": "test@test.org",
            "juntagrico-contact-content_type-object_id-0-sort_order": "0",
            "juntagrico-contact-content_type-object_id-0-id": str(self.email_contact.id),
            "juntagrico-contact-content_type-object_id-0-polymorphic_ctype":
                str(self.email_contact.polymorphic_ctype_id),
            "juntagrico-contact-content_type-object_id-1-member": str(self.new_contact.pk),
            "juntagrico-contact-content_type-object_id-1-display": "B",
            "juntagrico-contact-content_type-object_id-1-sort_order": "0",
            "juntagrico-contact-content_type-object_id-1-id": str(self.member_contact.id),
            "juntagrico-contact-content_type-object_id-1-polymorphic_ctype":
                str(self.member_contact.polymorphic_ctype_id),
            "juntagrico-contact-content_type-object_id-2-email": "test2@test.org",
            "juntagrico-contact-content_type-object_id-2-sort_order": "0",
            "juntagrico-contact-content_type-object_id-2-id": "",
            "juntagrico-contact-content_type-object_id-2-polymorphic_ctype":
                str(self.email_contact.polymorphic_ctype_id),
            "_saveasnew": 'yes'
        }
        self.assertPost(reverse('admin:action-copy-job', args=(self.complex_job.pk,)),
                        data=data, code=302)
        self.complex_job.refresh_from_db()
        # check that original job is unchanged
        self.assertEqual(self.complex_job.type, self.complex_job_data['type'])
        self.assertEqual(self.complex_job.slots, self.complex_job_data['slots'])
        self.assertEqual(self.complex_job.infinite_slots, self.complex_job_data['infinite_slots'])
        self.assertEqual(self.complex_job.time, self.complex_job_data['time'])
        self.assertEqual(self.complex_job.multiplier, self.complex_job_data['multiplier'])
        self.assertEqual(self.complex_job.additional_description, self.complex_job_data['additional_description'])
        self.assertEqual(self.complex_job.duration_override, self.complex_job_data['duration_override'])
        self.assertListEqual(self.complex_job.get_emails(), ['test@test.org', self.member2.email])
        # check completeness of copy
        new_job = RecuringJob.objects.last()
        self.assertEqual(new_job.type, self.complex_job.type)
        self.assertEqual(new_job.slots, 2)
        self.assertEqual(new_job.infinite_slots, False)
        dt = datetime.datetime.fromisoformat(str(self.new_date) + 'T13:46:46')
        if settings.USE_TZ:
            dt = dt.astimezone(timezone.get_default_timezone())
        self.assertEqual(new_job.time, dt)
        self.assertEqual(new_job.multiplier, 3.0)
        self.assertEqual(new_job.additional_description, "New Description")
        self.assertEqual(new_job.duration_override, 9)
        self.assertListEqual(sorted(new_job.get_emails()), [self.new_contact.email, 'test2@test.org'])

    def testMassCopyJob(self):
        self.assertGet(reverse('admin:action-mass-copy-job', args=(self.complex_job.pk,)))
        # test mass job copy changing entries
        data = {
            "type": str(self.complex_job.type.pk),
            "slots": "2",
            "multiplier": "3.0",
            "additional_description": "New Description",
            "duration_override": "9",
            "weekdays": ["1", "2", "3", "4", "5", "6", "7"],
            "new_time": "13:46:46",
            "start_date": self.new_date,
            "end_date": str(datetime.date.fromisoformat(self.new_date) + datetime.timedelta(days=7)),
            "weekly": "7",
            "juntagrico-contact-content_type-object_id-TOTAL_FORMS": "3",
            "juntagrico-contact-content_type-object_id-INITIAL_FORMS": "2",
            "juntagrico-contact-content_type-object_id-MIN_NUM_FORMS": "0",
            "juntagrico-contact-content_type-object_id-MAX_NUM_FORMS": "1000",
            "juntagrico-contact-content_type-object_id-0-DELETE": "on",
            "juntagrico-contact-content_type-object_id-0-email": "test@test.org",
            "juntagrico-contact-content_type-object_id-0-sort_order": "0",
            "juntagrico-contact-content_type-object_id-0-id": str(self.email_contact.id),
            "juntagrico-contact-content_type-object_id-0-polymorphic_ctype":
                str(self.email_contact.polymorphic_ctype_id),
            "juntagrico-contact-content_type-object_id-1-member": str(self.new_contact.pk),
            "juntagrico-contact-content_type-object_id-1-display": "B",
            "juntagrico-contact-content_type-object_id-1-sort_order": "0",
            "juntagrico-contact-content_type-object_id-1-id": str(self.member_contact.id),
            "juntagrico-contact-content_type-object_id-1-polymorphic_ctype":
                str(self.member_contact.polymorphic_ctype_id),
            "juntagrico-contact-content_type-object_id-2-email": "test2@test.org",
            "juntagrico-contact-content_type-object_id-2-sort_order": "0",
            "juntagrico-contact-content_type-object_id-2-id": "",
            "juntagrico-contact-content_type-object_id-2-polymorphic_ctype":
                str(self.email_contact.polymorphic_ctype_id),
        }
        self.assertPost(reverse('admin:action-mass-copy-job', args=(self.complex_job.pk,)),
                        data=data, code=302)
        self.complex_job.refresh_from_db()
        # check that original job is unchanged
        self.assertEqual(self.complex_job.type, self.complex_job_data['type'])
        self.assertEqual(self.complex_job.slots, self.complex_job_data['slots'])
        self.assertEqual(self.complex_job.infinite_slots, self.complex_job_data['infinite_slots'])
        self.assertEqual(self.complex_job.time, self.complex_job_data['time'])
        self.assertEqual(self.complex_job.multiplier, self.complex_job_data['multiplier'])
        self.assertEqual(self.complex_job.additional_description, self.complex_job_data['additional_description'])
        self.assertEqual(self.complex_job.duration_override, self.complex_job_data['duration_override'])
        self.assertListEqual(self.complex_job.get_emails(), ['test@test.org', self.member2.email])
        # check first and last new copy
        for new_job, new_date in zip(RecuringJob.objects.order_by("-pk")[0:8:7], (data['end_date'], data['start_date']), strict=True):
            self.assertEqual(new_job.type, self.complex_job.type)
            self.assertEqual(new_job.slots, 2)
            self.assertEqual(new_job.infinite_slots, False)
            dt = datetime.datetime.fromisoformat(new_date + 'T' + data['new_time'])
            if settings.USE_TZ:
                dt = dt.astimezone(timezone.get_default_timezone())
            self.assertEqual(new_job.time, dt)
            self.assertEqual(new_job.multiplier, 3.0)
            self.assertEqual(new_job.additional_description, "New Description")
            self.assertEqual(new_job.duration_override, 9)
            self.assertListEqual(sorted(new_job.get_emails()), [self.new_contact.email, 'test2@test.org'])


class JobCopyByAreaAdminTests(AreaAdminTestMixin, JobCopyTests):
    pass


@override_settings(USE_TZ=False)
class JobCopyWoTimezoneTests(JobCopyTests):
    pass


class OnetimeJobCopyTests(JuntagricoTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        time = timezone.now() + timezone.timedelta(hours=2)
        cls.other_location = cls.create_location('other_location')
        cls.complex_job_data = {
            'name': 'one_time_job',
            'activityarea': cls.area,
            'description': 'one_time_job_description',
            'default_duration': 2,
            'location': cls.create_location('one_time_location'),
            'slots': 1,
            'time': time,
            'infinite_slots': True,
            'multiplier': 2,
        }
        cls.complex_job = OneTimeJob.objects.create(**cls.complex_job_data)
        cls.email_contact = EmailContact(email='test@test.org')
        cls.member_contact = MemberContact(member=cls.member2, display=MemberContact.DISPLAY_EMAIL)
        cls.complex_job.contact_set.add(cls.email_contact, bulk=False)
        cls.complex_job.contact_set.add(cls.member_contact, bulk=False)

        cls.default_member = cls.admin
        cls.new_area = cls.area2
        cls.new_date = '2025-12-18'
        cls.new_contact = cls.member

    def testCopyJob(self):
        self.assertGet(reverse('admin:action-copy-onetime-job', args=(self.complex_job.pk,)))
        # test job copy changing entries
        data = {
            'name': 'one_time_job2',
            'activityarea': str(self.new_area.id),
            'description': 'one_time_job_description2',
            'default_duration': 3,
            'location': str(self.other_location.id),
            'slots': '2',
            'multiplier': '3.0',
            'time_0': self.new_date, 'time_1': '13:46:46',
            'juntagrico-contact-content_type-object_id-TOTAL_FORMS': '3',
            'juntagrico-contact-content_type-object_id-INITIAL_FORMS': '2',
            'juntagrico-contact-content_type-object_id-MIN_NUM_FORMS': '0',
            'juntagrico-contact-content_type-object_id-MAX_NUM_FORMS': '1000',
            'juntagrico-contact-content_type-object_id-0-DELETE': 'on',
            'juntagrico-contact-content_type-object_id-0-email': 'test@test.org',
            'juntagrico-contact-content_type-object_id-0-sort_order': '0',
            'juntagrico-contact-content_type-object_id-0-id': str(self.email_contact.id),
            'juntagrico-contact-content_type-object_id-0-polymorphic_ctype':
                str(self.email_contact.polymorphic_ctype_id),
            'juntagrico-contact-content_type-object_id-1-member': str(self.new_contact.pk),
            'juntagrico-contact-content_type-object_id-1-display': 'B',
            'juntagrico-contact-content_type-object_id-1-sort_order': '0',
            'juntagrico-contact-content_type-object_id-1-id': str(self.member_contact.id),
            'juntagrico-contact-content_type-object_id-1-polymorphic_ctype':
                str(self.member_contact.polymorphic_ctype_id),
            'juntagrico-contact-content_type-object_id-2-email': 'test2@test.org',
            'juntagrico-contact-content_type-object_id-2-sort_order': '0',
            'juntagrico-contact-content_type-object_id-2-id': '',
            'juntagrico-contact-content_type-object_id-2-polymorphic_ctype':
                str(self.email_contact.polymorphic_ctype_id),
            'job_extras_set-TOTAL_FORMS': 0, 'job_extras_set-INITIAL_FORMS': 0,
            '_saveasnew': 'yes'
        }
        self.assertPost(reverse('admin:action-copy-onetime-job', args=(self.complex_job.pk,)),
                        data=data, code=302)
        self.complex_job.refresh_from_db()
        # check that original job is unchanged
        self.assertEqual(self.complex_job.name, self.complex_job_data['name'])
        self.assertEqual(self.complex_job.activityarea, self.complex_job_data['activityarea'])
        self.assertEqual(self.complex_job.description, self.complex_job_data['description'])
        self.assertEqual(self.complex_job.default_duration, self.complex_job_data['default_duration'])
        self.assertEqual(self.complex_job.location, self.complex_job_data['location'])
        self.assertEqual(self.complex_job.slots, self.complex_job_data['slots'])
        self.assertEqual(self.complex_job.infinite_slots, self.complex_job_data['infinite_slots'])
        self.assertEqual(self.complex_job.time, self.complex_job_data['time'])
        self.assertEqual(self.complex_job.multiplier, self.complex_job_data['multiplier'])
        self.assertListEqual(self.complex_job.get_emails(), ['test@test.org', self.member2.email])
        # check completeness of copy
        new_job = OneTimeJob.objects.last()
        self.assertEqual(new_job.name, 'one_time_job2')
        self.assertEqual(new_job.activityarea, self.new_area)
        self.assertEqual(new_job.description, 'one_time_job_description2')
        self.assertEqual(new_job.default_duration, 3)
        self.assertEqual(new_job.location, self.other_location)
        self.assertEqual(new_job.slots, 2)
        self.assertEqual(new_job.infinite_slots, False)
        dt = datetime.datetime.fromisoformat(str(self.new_date) + 'T13:46:46')
        if settings.USE_TZ:
            dt = dt.astimezone(timezone.get_default_timezone())
        self.assertEqual(new_job.time, dt)
        self.assertEqual(new_job.multiplier, 3.0)
        self.assertListEqual(sorted(new_job.get_emails()), [self.new_contact.email, 'test2@test.org'])


class OnetimeJobCopyByAreaAdminTests(AreaAdminTestMixin, OnetimeJobCopyTests):
    pass


class JobConvertionTests(JuntagricoJobTestCase):
    def testConvertionToRecurringJob(self):
        selected_items = [self.complex_one_time_job.pk]
        self.assertPost(
            reverse('admin:juntagrico_onetimejob_changelist'),
            data={'action': 'transform_job', '_selected_action': selected_items},
            member=self.admin,
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

    def testConvertionToOneTimeJobs(self):
        selected_items = [self.complex_job_type.pk]
        self.assertPost(
            reverse('admin:juntagrico_jobtype_changelist'),
            data={'action': 'transform_job_type', '_selected_action': selected_items},
            member=self.admin,
            code=302
        )
        # check that original job was removed
        self.assertFalse(JobType.objects.filter(pk=self.complex_job_type.pk).exists())
        self.assertFalse(RecuringJob.objects.filter(pk=self.complex_job.pk).exists())
        # check if new job is complete
        new_job = OneTimeJob.objects.last()
        self.assertEqual(new_job.displayed_name, 'complex_job_type_name')
        self.assertEqual(new_job.default_duration, 6)  # override from job
        self.assertEqual(new_job.activityarea, self.area2)
        self.assertEqual(new_job.slots, 1)
        self.assertEqual(new_job.description, 'complex_job_type_description\nExtra Description')
        self.assertListEqual(sorted(new_job.get_emails()), [self.member2.email, 'test@test.org'])
        self.assertSetEqual(new_job.participant_emails, {self.member2.email})


class AdminTests(JuntagricoTestCase):
    def testDeliveryCopyForm(self):
        initial_count = Delivery.objects.all().count()
        data = {'subscription_bundle': self.bundle.pk,
                'delivery_date': '26.07.2020',
                }
        form = DeliveryCopyForm(instance=self.delivery1, data=data)
        form.full_clean()
        form.clean()
        form.save_m2m()
        form.save()
        self.assertEqual(Delivery.objects.all().count(), initial_count + 1)

    def testLocationReplaceForm(self):
        old_location = self.one_time_job1.location
        new_location = self.create_location('new_location')
        data = {'replace_by': new_location}
        form = LocationReplaceForm(queryset=Location.objects.filter(pk=old_location.pk), data=data)
        form.full_clean()
        form.clean()
        form.save()
        self.one_time_job1.refresh_from_db()
        self.assertEqual(self.one_time_job1.location, new_location)
        with self.assertRaises(Location.DoesNotExist):
            Location.objects.get(pk=old_location.pk)
