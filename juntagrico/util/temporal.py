import datetime

from django.utils import timezone

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


def start_of_year():
    year = timezone.now().year
    return datetime.date(year, 1, 1)


def start_of_next_year():
    year = timezone.now().year + 1
    return datetime.date(year, 1, 1)
