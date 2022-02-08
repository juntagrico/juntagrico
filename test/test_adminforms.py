import datetime

from django.core.exceptions import ValidationError

from juntagrico.admins.forms.delivery_copy_form import DeliveryCopyForm
from juntagrico.admins.forms.job_copy_form import JobCopyForm
from juntagrico.admins.forms.location_replace_form import LocationReplaceForm
from juntagrico.entity.delivery import Delivery
from juntagrico.entity.jobs import RecuringJob
from juntagrico.entity.location import Location
from test.util.test import JuntagricoTestCase


class AdminTests(JuntagricoTestCase):

    def testCopyJobForm(self):
        initial_count = RecuringJob.objects.all().count()
        data = {'type': self.job1.type.pk,
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '26.07.2020',
                'end_date': '26.07.2020',
                'weekly': '7'
                }
        form = JobCopyForm(instance=self.job1, data=data)
        form.full_clean()
        with self.assertRaises(ValidationError):
            form.clean()
        self.job1.time = datetime.datetime.now()
        data = {'type': self.job1.type.pk,
                'time': '05:04:53',
                'slots': '2',
                'weekdays': ['1'],
                'start_date': '01.07.2020',
                'end_date': '07.07.2020',
                'weekly': '7'
                }
        form = JobCopyForm(instance=self.job1, data=data)
        form.full_clean()
        form.clean()
        form.save_m2m()
        form.save()
        self.assertEqual(RecuringJob.objects.all().count(), initial_count + 1)
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
        data = {'replace_by': self.location}
        form = LocationReplaceForm(queryset=Location.objects.filter(pk=self.location2.pk), data=data)
        form.full_clean()
        form.clean()
        form.save()
        self.one_time_job1.refresh_from_db()
        self.assertEqual(self.one_time_job1.location, self.location)
        self.job_type2.refresh_from_db()
        self.assertEqual(self.job_type2.location, self.location)
        with self.assertRaises(Location.DoesNotExist):
            Location.objects.get(pk=self.location2.pk)
