import datetime

from django.core.exceptions import ValidationError

from juntagrico.admins.forms.job_copy_form import JobCopyForm
from juntagrico.entity.jobs import RecuringJob
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
