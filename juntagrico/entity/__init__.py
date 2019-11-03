from django.db import models
from django.utils.translation import gettext as _
from polymorphic.models import PolymorphicModel


def include_notification_permissions(entity_name, permissions=None):
    return list(permissions or []) + [
        (f'notified_on_{entity_name}_creation', _('Wird bei Erstellung informiert')),
        (f'notified_on_{entity_name}_cancellation', _('Wird bei Kündigung informiert'))
    ]


class OldHolder:
    '''find a better name'''
    _old = None


class JuntagricoBaseModel(models.Model, OldHolder):

    class Meta:
        abstract = True


class JuntagricoBasePoly(PolymorphicModel, OldHolder):

    class Meta:
        abstract = True