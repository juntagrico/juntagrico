from django.db import models
from django.utils.translation import gettext as _
from polymorphic.models import PolymorphicModel


def include_notification_permissions(entity_name, verbose_name, permissions=None):
    return list(permissions or []) + [
        (f'notified_on_{entity_name}_creation', _('Wird bei {0} Erstellung informiert').format(verbose_name)),
        (f'notified_on_{entity_name}_cancellation', _('Wird bei {0} Kündigung informiert').format(verbose_name))
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


def notifiable(cls):
    name = cls.__qualname__.split('.')[0].lower()
    cls.permissions = include_notification_permissions(name, cls.verbose_name, cls.permissions)
    return cls
