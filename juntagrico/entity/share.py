from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import notifiable
from juntagrico.entity.billing import Billable
from juntagrico.lifecycle.share import check_share_consistency

reason_for_acquisition_choices = ((1, _('Gründungsmitglied')),
                                  (2, _('Beitrittserklärung')),
                                  (3, _('Beitritts- und Übertragungserklärung')))

reason_for_cancellation_choices = ((1, _('Kündigung')),
                                   (2, _('Kündigung und Übertragungserklärung')),
                                   (3, _('Ausschluss')),
                                   (4, _('Tod')))


def share_value_default():
    return float(Config.share_price())


class Share(Billable):
    member = models.ForeignKey('Member', blank=True, on_delete=models.PROTECT)
    value = models.DecimalField(_('Wert'), max_digits=8, decimal_places=2, default=share_value_default)
    creation_date = models.DateField(_('Erzeugt am'), null=True, blank=True, default=timezone.now)
    paid_date = models.DateField(_('Bezahlt am'), null=True, blank=True)
    issue_date = models.DateField(_('Ausgestellt am'), null=True, blank=True)
    booking_date = models.DateField(_('Eingebucht am'), null=True, blank=True)
    cancelled_date = models.DateField(_('Gekündigt am'), null=True, blank=True)
    termination_date = models.DateField(
        _('Gekündigt auf'), null=True, blank=True)
    payback_date = models.DateField(
        _('Zurückbezahlt am'), null=True, blank=True)
    number = models.IntegerField(
        _('Anteilschein Nummer'), null=True, blank=True)
    sent_back = models.BooleanField(_('Zurückgesandt'), default=False)
    reason_for_acquisition = models.PositiveIntegerField(
        _('Grund des Erwerbs'), null=True, blank=True, choices=reason_for_acquisition_choices)
    reason_for_cancellation = models.PositiveIntegerField(
        _('Grund der Kündigung'), null=True, blank=True, choices=reason_for_cancellation_choices)
    notes = models.TextField(
        _('Notizen'), max_length=1000, default='', blank=True,
        help_text=_('Notizen für Administration. Nicht sichtbar für {}'.format(Config.vocabulary('member'))))

    __state_text_dict = {0: _('unbezahlt'),
                         1: _('bezahlt'),
                         3: _('gekündigt'),
                         7: _('zurückerstattet')}

    @property
    def state_text(self):
        now = timezone.now().date()
        paid = (self.paid_date is not None and self.paid_date <= now) << 0
        cancelled = (self.cancelled_date is not None and self.cancelled_date <= now) << 1
        paid_back = (self.payback_date is not None and self.payback_date <= now) << 2
        state_code = paid + cancelled + paid_back
        return Share.__state_text_dict.get(state_code, _('Fehler!'))

    @property
    def identifier(self):
        return self.number if self.number is not None else self.pk

    def clean(self):
        check_share_consistency(self)

    def __str__(self):
        return _('Anteilschein {0}').format(self.id)

    @notifiable
    class Meta:
        verbose_name = Config.vocabulary('share')
        verbose_name_plural = Config.vocabulary('share_pl')
