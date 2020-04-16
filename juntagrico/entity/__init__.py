from django.db import models
from django.utils import timezone
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


class SimpleStateModel(models.Model):

    activation_date = models.DateField(_('Aktivierungssdatum'), null=True, blank=True)
    cancellation_date = models.DateField(_('Kündigüngssdatum'), null=True, blank=True)
    deactivation_date = models.DateField(_('Deaktivierungssdatum'), null=True, blank=True)

    def activate(self, time=None):
        now = time or timezone.now().date()
        self.activation_date = self.activation_date or now
        self.save()

    def cancel(self, time=None):
        now = time or timezone.now().date()
        self.cancellation_date = self.cancellation_date or now
        self.save()

    def deactivate(self, time=None):
        now = time or timezone.now().date()
        self.deactivation_date = self.deactivation_date or now
        self.save()

    @property
    def active(self):
        return self.state == 'active'

    @property
    def state(self):
        result = 'error'
        if self.activation_date is None and self.deactivation_date is None and self.deactivation_date is None:
            result = 'waiting'
        elif self.activation_date is not None and self.deactivation_date is None and self.deactivation_date is None:
            result = 'active'
        elif self.activation_date is not None and self.deactivation_date is not None and self.deactivation_date is None:
            result = 'canceled'
        elif self.activation_date is not None and self.deactivation_date is not None and self.deactivation_date is not None:
            result = 'inactive'
        return result

    @property
    def state_text(self):
        result = _('Fehler!')
        if self.activation_date is None and self.deactivation_date is None and self.deactivation_date is None:
            result = _('wartend')
        elif self.activation_date is not None and self.deactivation_date is None and self.deactivation_date is None:
            result = _('aktiv')
        elif self.activation_date is not None and self.deactivation_date is not None and self.deactivation_date is None:
            result = _('aktiv - gekündigt')
        elif self.activation_date is not None and self.deactivation_date is not None and self.deactivation_date is not None:
            result = _('inaktiv-gekündigt')
        return result

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
