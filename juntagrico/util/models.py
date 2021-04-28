'''
    Copys the user defined attributes of a model into another model.
    It will only copy the fields with are present in both
'''
from django.db.models import Q, QuerySet
from django.utils import timezone


def attribute_copy(source, target):
    for field in target._meta.fields:
        if field.auto_created is False and \
                field.editable is True and \
                field.attname in source.__dict__ and \
                field.attname in target.__dict__:
            target.__dict__[field.attname] = source.__dict__[field.attname]


def q_activated():
    return Q(activation_date__isnull=False, activation_date__lte=timezone.now().date())


def q_cancelled():
    return Q(cancellation_date__isnull=False, cancellation_date__lte=timezone.now().date())


def q_deactivated():
    return Q(deactivation_date__isnull=False, deactivation_date__lte=timezone.now().date())


def q_isactive():
    return q_activated() & ~q_deactivated()


def q_deactivation_planned():
    return Q(deactivation_date__isnull=False)


class PropertyQuerySet(QuerySet):

    def __init__(self, model, query, using, hints):
        super().__init__(model, query, using, hints)
        self.properties = {}

    @staticmethod
    def from_qs(queryset):
        return PropertyQuerySet(queryset.model, queryset.query.chain(), queryset._db, queryset._hints)

    def set_property(self, key, value):
        self.properties[key] = value

    def get_property(self, key):
        return self.properties.get(key)

    def _clone(self):
        result = super()._clone()
        result.properties = self.properties.copy()
        return result
