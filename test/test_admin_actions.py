from django.urls import reverse
from test.util.test import JuntagricoTestCase


class AdminActionTests(JuntagricoTestCase):

    def testMassCopyJob(self):
        self.assertGet(reverse('admin:action-mass-copy-job', args=(self.job1.pk,)), member=self.admin)
        self.assertPost(reverse('admin:action-mass-copy-job', args=(self.job1.pk,)),
                        data={'start_date': '22.01.2022',
                              'end_date': '30.01.2022',
                              'weekdays': ['1'],
                              'weekly': '7'},
                        member=self.admin)
