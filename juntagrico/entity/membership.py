
from django.db import models
from django.utils.translation import gettext_lazy as _, gettext

from juntagrico.config import Config
from juntagrico.entity import notifiable, SimpleStateModel
from juntagrico.lifecycle.membership import check_membership_consistency
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

    def clean(self):
        return check_membership_consistency(self)
