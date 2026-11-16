from django.utils import dateparse


def parse_date(date):
    return dateparse.parse_date(date) if isinstance(date, str) else date
