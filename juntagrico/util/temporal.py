import calendar
import datetime
from datetime import timedelta

from django.utils import timezone
from django.utils.timezone import get_default_timezone as gdtz
from django.utils.translation import gettext as _

from juntagrico.config import Config

weekday_choices = ((1, _('Montag')),
                   (2, _('Dienstag')),
                   (3, _('Mittwoch')),
                   (4, _('Donnerstag')),
                   (5, _('Freitag')),
                   (6, _('Samstag')),
                   (7, _('Sonntag')))

weekdays = dict(weekday_choices)


def is_date_in_cancelation_period(date):
    return start_of_business_year() <= date <= cancelation_date()


def weekday_short(day, num):
    weekday = weekdays[day]
    return weekday[:num]


def start_of_business_year():
    day = Config.business_year_start()['day']
    month = Config.business_year_start()['month']
    return calculate_last(day, month)


def end_of_business_year():
    return start_of_next_business_year() - timedelta(days=1)


def start_of_next_business_year():
    day = Config.business_year_start()['day']
    month = Config.business_year_start()['month']
    return calculate_next(day, month)


def end_of_next_business_year():
    tmp = start_of_next_business_year()
    return datetime.datetime(tmp.year + 1, tmp.month, tmp.day, tzinfo=gdtz()) - timedelta(days=1)


def start_of_specific_business_year(refdate):
    day = Config.business_year_start()['day']
    month = Config.business_year_start()['month']
    return calculate_last_offset(day, month, refdate)


def end_of_specific_business_year(refdate):
    day = Config.business_year_start()['day']
    month = Config.business_year_start()['month']

    # calculate_next_offset of start of business year stays the same date
    # we need to offset refdate by one day in this case
    if refdate.month == month and refdate.day == day:
        refdate = refdate + timedelta(days=1)

    return calculate_next_offset(day, month, refdate) - timedelta(days=1)


def next_cancelation_date():
    now = timezone.now()
    c_month = Config.business_year_cancelation_month()
    if now.month < c_month + 1:
        year = now.year
    else:
        year = now.year + 1
    return datetime.datetime(year, c_month, calendar.monthrange(year, c_month)[1], tzinfo=gdtz())


def cancelation_date():
    start = start_of_business_year()
    c_month = Config.business_year_cancelation_month()
    if start.month < c_month + 1:
        year = start.year
    else:
        year = start.year + 1
    return datetime.datetime(year, c_month, calendar.monthrange(year, c_month)[1], tzinfo=gdtz())


def next_membership_end_date():
    now = timezone.now()
    month = Config.membership_end_month()
    if now <= cancelation_date():
        offset = end_of_business_year()
    else:
        offset = end_of_next_business_year()
    day = calendar.monthrange(offset.year, month)[1]
    return calculate_next_offset(day, month, offset)


def calculate_next(day, month):
    now = timezone.now()
    if now.month < month or (now.month == month and now.day <= day):
        year = now.year
    else:
        year = now.year + 1
    return datetime.datetime(year, month, day, tzinfo=gdtz())


def calculate_last(day, month):
    now = timezone.now()
    if now.month > month or (now.month == month and now.day >= day):
        year = now.year
    else:
        year = now.year - 1
    return datetime.datetime(year, month, day, tzinfo=gdtz())


def calculate_next_offset(day, month, offset):
    if offset.month < month or (offset.month == month and offset.day <= day):
        year = offset.year
    else:
        year = offset.year + 1
    return datetime.datetime(year, month, day, tzinfo=gdtz())


def calculate_last_offset(day, month, offset):
    if offset.month > month or (offset.month == month and offset.day >= day):
        year = offset.year
    else:
        year = offset.year - 1
    return datetime.datetime(year, month, day, tzinfo=gdtz())


month_choices = ((1, _('Januar')),
                 (2, _('Februar')),
                 (3, _('März')),
                 (4, _('April')),
                 (5, _('Mai')),
                 (6, _('Juni')),
                 (7, _('Juli')),
                 (8, _('August')),
                 (9, _('September')),
                 (10, _('Oktober')),
                 (11, _('November')),
                 (12, _('Dezember')))
