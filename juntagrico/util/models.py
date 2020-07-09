'''
    Copys the user defined attributes of a model into another model.
    It will only copy the fields with are present in both
'''
from django.db.models import Q
from django.utils import timezone


def attribute_copy(source, target):
    for field in target._meta.fields:
        if field.auto_created is False and \
           field.editable is True and \
           field.attname in source.__dict__ and \
           field.attname in target.__dict__:
            target.__dict__[field.attname] = source.__dict__[field.attname]


q_activated = Q(activation_date__isnull=False, activation_date__lte=timezone.now().date())


q_cancelled = Q(cancellation_date__isnull=False, cancellation_date__lte=timezone.now().date())


q_deactivated = Q(deactivation_date__isnull=False, deactivation_date__lte=timezone.now().date())
