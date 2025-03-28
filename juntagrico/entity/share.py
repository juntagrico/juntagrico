import datetime

from django.db import models
from django.utils.translation import gettext as _
from polymorphic.managers import PolymorphicManager

from juntagrico.config import Config
from juntagrico.entity import notifiable
from juntagrico.entity.billing import Billable
from juntagrico.lifecycle.share import check_share_consistency
from juntagrico.queryset.share import ShareQueryset
from juntagrico.util.temporal import next_membership_end_date

reason_for_acquisition_choices = ((1, _('Gründungsmitglied')),
                                  (2, _('Beitrittserklärung')),
                                  (3, _('Beitritts- und Übertragungserklärung')),
                                  (4, _('Übertragungserklärung')),
                                  (5, _('Erhöhung der Anteile')),
                                  (6, _('Betriebsbeteiligung - Lohn')))

reason_for_cancellation_choices = ((1, _('Kündigung')),
                                   (2, _('Kündigung und Übertragungserklärung')),
                                   (3, _('Ausschluss')),
                                   (4, _('Tod')))


def share_value_default():
    return float(Config.share_price())


class Share(Billable):
    member = models.ForeignKey('Member', on_delete=models.PROTECT)
    value = models.DecimalField(_('Wert'), max_digits=8, decimal_places=2, blank=True, default=share_value_default)
    creation_date = models.DateField(_('Erzeugt am'), null=True, blank=True, default=datetime.date.today)
    paid_date = models.DateField(_('Bezahlt am'), null=True, blank=True)
    issue_date = models.DateField(_('Ausgestellt am'), null=True, blank=True)
    booking_date = models.DateField(_('Eingebucht am'), null=True, blank=True)
    cancelled_date = models.DateField(_('Gekündigt am'), null=True, blank=True)  # TODO: rename to cancellation_date
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
        _('Notizen'), default='', blank=True,
        help_text=_('Notizen für Administration. Nicht sichtbar für {}'.format(Config.vocabulary('member'))))

    objects = PolymorphicManager.from_queryset(ShareQueryset)()

    __state_text_dict = {0: _('unbezahlt'),
                         1: _('bezahlt'),
                         2: _('storniert'),
                         3: _('gekündigt'),
                         7: _('zurückerstattet')}

    @property
    def state_text(self):
        today = datetime.date.today()
        paid = (self.paid_date is not None and self.paid_date <= today) << 0
        canceled = (self.cancelled_date is not None and self.cancelled_date <= today) << 1
        paid_back = (self.payback_date is not None and self.payback_date <= today) << 2
        state_code = paid + canceled + paid_back
        return Share.__state_text_dict.get(state_code, _('Fehler!'))

    @property
    def identifier(self):
        return self.number if self.number is not None else self.pk

    def clean(self):
        check_share_consistency(self)

    def __str__(self):
        return _('Anteilschein {0} ({1})').format(self.id, self.state_text)

    def cancel(self, date=None, end_date=None):
        self.cancelled_date = self.cancelled_date or date or datetime.date.today()
        self.termination_date = self.termination_date or end_date or next_membership_end_date(self.cancelled_date)
        self.save()

    def payback(self, date=None):
        date = date or datetime.date.today()
        self.payback_date = date
        self.save()
        self.member.deactivate(date)

    @notifiable
    class Meta:
        verbose_name = Config.vocabulary('share')
        verbose_name_plural = Config.vocabulary('share_pl')
