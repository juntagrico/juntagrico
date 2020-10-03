from django.db import models
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import notifiable
from juntagrico.entity.billing import Billable
from juntagrico.lifecycle.share import check_share_consistency
from django.utils import timezone

class Share(Billable):
    member = models.ForeignKey('Member', blank=True, on_delete=models.PROTECT)
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
    notes = models.TextField(
        _('Notizen'), max_length=1000, default='', blank=True,
        help_text=_('Notizen für Administration. Nicht sichtbar für {}'.format(Config.vocabulary('member'))))

    def clean(self):
        check_share_consistency(self)

    def __str__(self):
        return _('Anteilschein {0}').format(self.id)

    @notifiable
    class Meta:
        verbose_name = Config.vocabulary('share')
        verbose_name_plural = Config.vocabulary('share_pl')
