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

    __state_text_dict = {0: _('wartend'),
                         1: _('aktiv'),
                         3: _('aktiv - gekündigt'),
                         7: _('inaktiv-gekündigt')}

    __state_dict = {0: 'waiting',
                    1: 'active',
                    3: 'canceled',
                    7: 'inactive'}

    creation_date = models.DateField(_('Erstellungsdatum'), null=True, blank=True, auto_now_add=True)
    activation_date = models.DateField(_('Aktivierungsdatum'), null=True, blank=True)
    cancellation_date = models.DateField(_('Kündigungsdatum'), null=True, blank=True)
    deactivation_date = models.DateField(_('Deaktivierungsdatum'), null=True, blank=True)

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
    def __state_code(self):
        now = timezone.now().date()
        active = (self.activation_date is not None and self.activation_date <= now) << 0
        cancelled = (self.cancellation_date is not None and self.cancellation_date <= now) << 1
        deactivated = (self.deactivation_date is not None and self.deactivation_date <= now) << 2
        return active + cancelled + deactivated

    @property
    def state(self):
        return SimpleStateModel.__state_dict.get(self.__state_code, 'error')

    @property
    def state_text(self):
        return SimpleStateModel.__state_text_dict.get(self.__state_code, _('Fehler!'))

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
