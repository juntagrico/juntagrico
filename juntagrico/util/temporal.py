import calendar
import datetime
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
    day = Config.business_year_start()["day"]
    month = Config.business_year_start()["month"]
    return calculate_last(day, month)

def start_of_next_business_year():
    day = Config.business_year_start()["day"]
    month = Config.business_year_start()["month"]
    return calculate_next(day, month)

def next_cancelation_date():
    now = timezone.now()
    c_month = Config.business_year_cancelation_month()
    if now.month<c_month+1:
        year=now.year
    else:
        year=now.year+1
    return datetime.date(year, c_month, calendar.monthrange(year,c_month)[1])

def calculate_next(day, month):
    now = timezone.now()
    if now.month<month or (now.month==month and now.day <= day):
        year=now.year
    else:
        year=now.year+1
    return datetime.date(year, c_month, day)  

def calculate_last(day, month):
    now = timezone.now()
    if now.month>month or (now.month==month and now.day >= day):
        year=now.year
    else:
        year=now.year-1
    return datetime.date(year, c_month, day)    
	
month_choices = ((1, "Januar"),
                   (2, "Februar"),
                   (3, "März"),
                   (4, "April"),
                   (5, "Mai"),
                   (6, "Juni"),
                   (7, "Juli"),
                   (8, "August"),
                   (9, "September"),
                   (10, "Oktober"),
                   (11, "November"),
                   (12, "Dezember"))
