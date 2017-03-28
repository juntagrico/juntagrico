import calendar
from django.utils import timezone

from juntagrico.config import Config

weekday_choices = ((1, "Montag"),
                   (2, "Dienstag"),
                   (3, "Mittwoch"),
                   (4, "Donnerstag"),
                   (5, "Freitag"),
                   (6, "Samstag"),
                   (7, "Sonntag"))

weekdays = dict(weekday_choices)


def get_status_image_text(percent=0):
    if percent >= 100:
        return "Fertig"
    elif percent >= 75:
        return "Dreiviertel"
    elif percent >= 50:
        return "Halb"
    elif percent > 0:
        return "Angefangen"
    else:
        return "Nix"


def start_of_business_year():
    now = timezone.now()
    day = Config.business_year_start()["day"]
    month = Config.business_year_start()["month"]
    if now.month<month:
        year=now.year-1
    else:
        year=now.year
    return timezone.date(year, month, day)

def start_of_next_business_year():
    now = timezone.now()
    day = Config.business_year_start()["day"]
    month = Config.business_year_start()["month"]
    if now.month<month:
        year=now.year
    else:
        year=now.year+1
    return timezone.date(year, month, day)

def next_cancelation_date():
    now = timezone.now()
    c_month = Config.business_year_cancelation_month()
    if now.month<c_month+1:
        year=now.year
    else:
        year=now.year+1
    return timezone.date(year, c_month, calendar.monthrange(year,c_month)[1])
