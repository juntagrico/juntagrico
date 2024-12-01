'''
    Copys the user defined attributes of a model into another model.
    It will only copy the fields with are present in both
'''
import datetime

from django.db.models import Q


def attribute_copy(source, target):
    for field in target._meta.fields:
        if field.auto_created is False and \
                field.editable is True and \
                field.attname in source.__dict__ and \
                field.attname in target.__dict__:
            target.__dict__[field.attname] = source.__dict__[field.attname]


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
