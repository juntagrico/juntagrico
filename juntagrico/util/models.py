import datetime

from django.db.models import Q


def q_activated():
    return Q(activation_date__isnull=False, activation_date__lte=datetime.date.today())


def q_canceled():
    return Q(cancellation_date__isnull=False, cancellation_date__lte=datetime.date.today())


def q_deactivated():
    return Q(deactivation_date__isnull=False, deactivation_date__lte=datetime.date.today())


def q_isactive():
    return q_activated() & ~q_deactivated()


def q_deactivation_planned():
    return Q(deactivation_date__isnull=False)
