from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import get_default_timezone as gdtz

from juntagrico.util.temporal import start_of_business_year
from juntagrico.util.temporal import start_of_specific_business_year,\
                                    end_of_specific_business_year


class BusinessYearTests(TestCase):

    def test_start_of_business_year(self):
        today = timezone.now()
        expected_start = datetime(today.year, 1, 1, tzinfo=gdtz())
        self.assertEqual(expected_start, start_of_business_year())

    def test_start_of_specific_business_year(self):
        self.assertEqual(datetime(2018, 1, 1, tzinfo=gdtz()),
                         start_of_specific_business_year(datetime(2018, 7, 24, tzinfo=gdtz())))
        self.assertEqual(datetime(2018, 1, 1, tzinfo=gdtz()),
                         start_of_specific_business_year(datetime(2018, 1, 1, tzinfo=gdtz())))
        self.assertEqual(datetime(2018, 1, 1, tzinfo=gdtz()),
                         start_of_specific_business_year(datetime(2018, 12, 31, tzinfo=gdtz())))

    def test_end_of_specific_business_year(self):
        self.assertEqual(datetime(2018, 12, 31, tzinfo=gdtz()),
                         end_of_specific_business_year(datetime(2018, 7, 24, tzinfo=gdtz())))
        self.assertEqual(datetime(2018, 12, 31, tzinfo=gdtz()),
                         end_of_specific_business_year(datetime(2018, 1, 1, tzinfo=gdtz())))
        self.assertEqual(datetime(2018, 12, 31, tzinfo=gdtz()),
                         end_of_specific_business_year(datetime(2018, 12, 31, tzinfo=gdtz())))
