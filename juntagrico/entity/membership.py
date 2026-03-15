import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _, gettext

from juntagrico.config import Config
from juntagrico.entity import notifiable, SimpleStateModel
from juntagrico.queryset.membership import MembershipQueryset


class Membership(SimpleStateModel):
    @notifiable
    class Meta:
        verbose_name = Config.vocabulary('membership')
        verbose_name_plural = Config.vocabulary('membership_pl')

    account = models.ForeignKey('Member', on_delete=models.PROTECT, related_name='memberships')
    number = models.IntegerField(_('Mitgliedschaftsnummer'), null=True, blank=True)
    notes = models.TextField(
        _('Notizen'), default='', blank=True,
        help_text=_('Notizen für Administration. Nicht sichtbar für {member_type}').format(
            member_type=Config.vocabulary('member_type')
        )
    )

    objects = MembershipQueryset.as_manager()

    def __str__(self):
        return gettext('{0} ({1})').format(self.id, self.state_text)

    def cancel(self, date=None, commit=True):
        date = date or datetime.date.today()
        self.cancellation_date = date
        # if all shares of member are already paid back and has no subscriptions: deactivate automatically
        member = self.account
        has_sub = member.subscription_current or member.subscription_future
        if not has_sub and not member.share_set.potentially_pending_payback().exists():
            self.deactivation_date = date
        for share in member.share_set.all():
            share.cancel(date)
        if commit:
            self.save()
