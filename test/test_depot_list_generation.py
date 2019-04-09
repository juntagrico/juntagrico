from django.test import TestCase
from django.core.management import call_command

from test.util.test_data import create_test_data


class DepotlistTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data(cls)

    def test_depot_list(self):
        call_command('generate_depot_list', '--force')
