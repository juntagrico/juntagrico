import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext as _
from polymorphic.models import PolymorphicModel
from schwifty import IBAN


class OldHolder:
    '''find a better name'''
    _old = None


class JuntagricoBaseModel(models.Model, OldHolder):

    class Meta:
        abstract = True


class JuntagricoBasePoly(PolymorphicModel, OldHolder):

    class Meta:
        abstract = True


class SimpleStateModelQuerySet(QuerySet):
    def active_on(self, date=None):
        date = date or datetime.date.today()
        return self.in_daterange(date, date)

    def in_daterange(self, from_date, till_date):
        """
        exclude those that ended before or started after our date range.
        """
        return self.filter(activation_date__lte=till_date).exclude(deactivation_date__lt=from_date)


class SimpleStateModel(models.Model):

    __state_text_dict = {0: _('wartend'),
                         1: _('aktiv'),
                         3: _('inaktiv')}

    __state_dict = {0: 'waiting',
                    1: 'active',
                    3: 'inactive'}

    creation_date = models.DateField(_('Erstellungsdatum'), null=True, blank=True, auto_now_add=True)
    activation_date = models.DateField(_('Aktivierungsdatum'), null=True, blank=True)
    cancellation_date = models.DateField(_('Kündigungsdatum'), null=True, blank=True)
    deactivation_date = models.DateField(_('Deaktivierungsdatum'), null=True, blank=True)

    def activate(self, date=None):
        date = date or datetime.date.today()
        self.activation_date = self.activation_date or date
        self.save()

    def cancel(self, date=None):
        today = datetime.date.today()
        if date is None or date > today:
            date = today
        self.cancellation_date = self.cancellation_date or date
        self.save()

    def deactivate(self, date=None):
        today = datetime.date.today()
        date = date or today
        self.activation_date = self.activation_date or date  # allows immediate deactivation
        if not self.cancellation_date:
            self.cancellation_date = today if date > today else date  # can't cancel in the future
        self.deactivation_date = self.deactivation_date or date
        self.save()

    @property
    def waiting(self):
        return self.state == 'waiting'

    @property
    def active(self):
        return self.state == 'active'

    @property
    def inactive(self):
        return self.state == 'inactive'

    @property
    def __state_code(self):
        today = datetime.date.today()
        active = (self.activation_date is not None and self.activation_date <= today) << 0
        deactivated = (self.deactivation_date is not None and self.deactivation_date <= today) << 1
        return active + deactivated

    @property
    def state(self):
        return SimpleStateModel.__state_dict.get(self.__state_code, 'error')

    @property
    def state_text(self):
        return SimpleStateModel.__state_text_dict.get(self.__state_code, _('Fehler!'))

    @property
    def canceled(self):
        # Sufficient to check if cancellation date is set, because it can not be in the future
        return self.cancellation_date is not None

    def check_date_order(self):
        today = datetime.date.today()
        is_active = self.activation_date is not None
        is_canceled = self.cancellation_date is not None
        is_deactivated = self.deactivation_date is not None
        if is_deactivated:
            if not is_active:
                raise ValidationError(_('Bitte "Aktivierungsdatum" ausfüllen'), code='missing_activation_date')
            elif self.activation_date > self.deactivation_date:
                raise ValidationError(_('"Aktivierungsdatum" kann nicht nach "Deaktivierungsdatum" liegen'), code='invalid')
            elif not is_canceled:
                raise ValidationError(_('Bitte "Kündigungsdatum" ausfüllen'), code='missing_cancellation_date')
            elif self.cancellation_date > self.deactivation_date:
                raise ValidationError(_('"Kündigungsdatum" kann nicht nach "Deaktivierungsdatum" liegen'), code='invalid')
        if is_canceled and self.cancellation_date > today:
            raise ValidationError(_('Das "Kündigungsdatum" kann nicht in der Zukunft liegen'), code='invalid')

    class Meta:
        abstract = True


class LowercaseEmailField(models.EmailField):
    """
    Override EmailField to convert emails to lowercase before saving.
    """
    def get_prep_value(self, value):
        """
        Convert email to lowercase.
        """
        # Value can be None so check that it's a string before lowercasing.
        if isinstance(value, str):
            return value.lower()
        return value


def notifiable(cls):
    entity_name = cls.__qualname__.split('.')[0].lower()
    new_permissions = list(getattr(cls, 'permissions', [])) + [
        (f'notified_on_{entity_name}_creation', _('Wird bei {0} Erstellung informiert').format(cls.verbose_name)),
        (f'notified_on_{entity_name}_cancellation', _('Wird bei {0} Kündigung informiert').format(cls.verbose_name))
    ]
    cls.permissions = new_permissions
    return cls


def absolute_url(*args, **kwargs):
    def wrapper(cls):
        def get_absolute_url(self):
            return reverse(kwargs['name'], args=[self.pk])
        cls.get_absolute_url = get_absolute_url
        return cls
    return wrapper


def validate_iban(value):
    if value != '' and not IBAN(value, True).is_valid:
        raise ValidationError(_('IBAN ist nicht gültig'))
