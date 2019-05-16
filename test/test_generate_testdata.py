from io import StringIO

from django.test import TestCase
from django.core.management import call_command

from test.util.test_data import create_test_data


class TestdataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def test_depot_list(self):
        out = StringIO()
        call_command('generate_testdata', '--force', stdout=out)
        self.assertEqual(out.getvalue(), '')
