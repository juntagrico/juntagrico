import datetime

from django.core.exceptions import ValidationError
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from juntagrico.admins.forms.delivery_copy_form import DeliveryCopyForm
from juntagrico.admins.forms.job_copy_form import JobCopyForm, JobCopyToFutureForm
from juntagrico.admins.forms.location_replace_form import LocationReplaceForm
from juntagrico.entity.delivery import Delivery
from juntagrico.entity.jobs import RecuringJob
from juntagrico.entity.location import Location
from . import JuntagricoTestCase
from ..entity.contact import EmailContact, MemberContact


class JobFormTests(JuntagricoTestCase):

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

    def testCopyJobForm(self):
        # test 0 copies (fails)
        initial_count = RecuringJob.objects.all().count()
        data = {'type': self.job1.type.pk,
                'time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '26.07.2020',
                'end_date': '26.07.2020',
                'weekly': '7'
                }
        form = JobCopyForm(instance=self.job1, data=data)
        form.full_clean()
        with self.assertRaises(ValidationError):
            # should raise, because no jobs are created in this date range
            form.clean()

        # test 1 copy
        self.complex_job.time = datetime.datetime.now()
        data = {'type': self.complex_job.type.pk,
                'time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '01.07.2020',
                'end_date': '07.07.2020',
                'weekly': '7'
                }
        form = JobCopyForm(instance=self.complex_job, data=data)
        form.full_clean()
        form.clean()
        form.save()
        self.assertEqual(RecuringJob.objects.all().count(), initial_count + 1)
        # check completeness of copy
        new_job = RecuringJob.objects.last()
        self.assertEqual(self.complex_job.type, new_job.type)
        self.assertEqual(self.complex_job.slots, new_job.slots)
        self.assertEqual(self.complex_job.infinite_slots, new_job.infinite_slots)
        dt = datetime.datetime.fromisoformat('2020-07-06T' + data['time'])
        if settings.USE_TZ:
            dt = dt.astimezone(timezone.get_default_timezone())
        self.assertEqual(dt, new_job.time)
        self.assertEqual(self.complex_job.multiplier, new_job.multiplier)
        self.assertEqual(self.complex_job.additional_description, new_job.additional_description)
        self.assertEqual(self.complex_job.duration_override, new_job.duration_override)
        # Test 2 copies
        data = {'type': self.job1.type.pk,
                'time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '01.07.2020',
                'end_date': '15.07.2020',
                'weekly': '14'
                }
        form = JobCopyForm(instance=self.job1, data=data)
        form.full_clean()
        form.save()
        self.assertEqual(RecuringJob.objects.all().count(), initial_count + 2)

    def testCopyJob(self):
        self.assertGet(reverse('admin:action-mass-copy-job', args=(self.complex_job.pk,)), member=self.admin)
        # test mass job copy changing entries
        data = {
            "type": str(self.complex_job.type.pk),
            "slots": "2",
            "multiplier": "3.0",
            "additional_description": "New Description",
            "duration_override": "9",
            "weekdays": "2",
            "time": "13:46:46",
            "start_date": "18.06.2024",
            "end_date": "19.06.2024",
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
            "juntagrico-contact-content_type-object_id-1-member": str(self.member.pk),
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
                        data=data, code=302, member=self.admin)
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
        dt = datetime.datetime.fromisoformat('2024-06-18T' + data['time'])
        if settings.USE_TZ:
            dt = dt.astimezone(timezone.get_default_timezone())
        self.assertEqual(new_job.time, dt)
        self.assertEqual(new_job.multiplier, 3.0)
        self.assertEqual(new_job.additional_description, "New Description")
        self.assertEqual(new_job.duration_override, 9)
        self.assertListEqual(new_job.get_emails(), [self.member.email, 'test2@test.org'])

    def testCopyJobToFutureForm(self):
        # test failing case
        initial_count = RecuringJob.objects.all().count()
        data = {'type': self.job1.type.pk,
                'time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '01.07.2020',
                'end_date': '07.07.2020',
                'weekly': '7'
                }
        form = JobCopyToFutureForm(instance=self.job1, data=data)
        form.full_clean()
        with self.assertRaises(ValidationError) as validation_error:
            # should raise, because jobs are in the past
            form.clean()
        self.assertEqual(validation_error.exception.code, 'date_in_past')

        today = datetime.date.today()
        # test successful case
        data = {'type': self.job1.type.pk,
                'time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': today + datetime.timedelta(1),
                'end_date': today + datetime.timedelta(7),
                'weekly': '7'
                }
        form = JobCopyToFutureForm(instance=self.job1, data=data)
        form.full_clean()
        form.clean()
        form.save()
        self.assertEqual(RecuringJob.objects.all().count(), initial_count + 1)


@override_settings(USE_TZ=False)
class JobFormWoTimezoneTests(JobFormTests):
    pass


class AdminTests(JuntagricoTestCase):
    def testDeliveryCopyForm(self):
        initial_count = Delivery.objects.all().count()
        data = {'subscription_size': self.sub_size.pk,
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
