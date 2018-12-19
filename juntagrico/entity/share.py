# encoding: utf-8

from django.utils.translation import gettext as _

from juntagrico.entity.billing import *
from juntagrico.util.bills import *
from juntagrico.config import Config


class Share(Billable):
    member = models.ForeignKey('Member', blank=True, on_delete=models.PROTECT)
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
    notes = models.TextField(
        _('Notizen'), max_length=1000, default='', blank=True)

    @classmethod
    def create(cls, sender, instance, created, **kwds):
        if created and Config.billing():
            bill_share(instance)

    def __str__(self):
        return _('Anteilschein #%s') % self.id

    class Meta:
        verbose_name = Config.vocabulary('share')
        verbose_name_plural = Config.vocabulary('share_pl')
