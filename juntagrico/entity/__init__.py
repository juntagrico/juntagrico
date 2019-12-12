from django.db import models
from django.utils.translation import gettext as _
from polymorphic.models import PolymorphicModel


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
    entity_name = cls.__qualname__.split('.')[0].lower()
    new_permissions = list(getattr(cls, 'permissions', [])) + [
        (f'notified_on_{entity_name}_creation', _('Wird bei {0} Erstellung informiert').format(cls.verbose_name)),
        (f'notified_on_{entity_name}_cancellation', _('Wird bei {0} Kündigung informiert').format(cls.verbose_name))
    ]
    cls.permissions = new_permissions
    return cls
