from datetime import date

from django.test import TestCase
from django.utils import timezone

from juntagrico.util.temporal import start_of_business_year
from juntagrico.util.temporal import start_of_specific_business_year, \
    end_of_specific_business_year


class BusinessYearTests(TestCase):

    def test_start_of_business_year(self):
        today = timezone.now()
        expected_start = date(today.year, 1, 1)
        self.assertEqual(expected_start, start_of_business_year())

    def test_start_of_specific_business_year(self):
        self.assertEqual(date(2018, 1, 1),
                         start_of_specific_business_year(date(2018, 7, 24)))
        self.assertEqual(date(2018, 1, 1),
                         start_of_specific_business_year(date(2018, 1, 1)))
        self.assertEqual(date(2018, 1, 1),
                         start_of_specific_business_year(date(2018, 12, 31)))

    def test_end_of_specific_business_year(self):
        self.assertEqual(date(2018, 12, 31),
                         end_of_specific_business_year(date(2018, 7, 24)))
        self.assertEqual(date(2018, 12, 31),
                         end_of_specific_business_year(date(2018, 1, 1)))
        self.assertEqual(date(2018, 12, 31),
                         end_of_specific_business_year(date(2018, 12, 31)))
