from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext as _

from juntagrico.entity.subs import SubscriptionPart
from juntagrico.config import Config


class SubscriptionPartInlineFormset(BaseInlineFormSet):
    def clean(self):
        required_shares = 0
        for form in self.forms:
            if form.instance.pk:
                required_shares += form.instance.type.shares
        available_shares = sum([member.active_shares_count for member in self.instance._future_members])
        if required_shares > available_shares:
            raise ValidationError(
                _('Nicht genug {0} vorhanden. Vorhanden {1}. Benötigt {2}').format(Config.vocabulary('share_pl'),
                                                                                   available_shares,
                                                                                   required_shares),
                code='invalid')


class SubscriptionPartInline(admin.TabularInline):
    formset = SubscriptionPartInlineFormset
    model = SubscriptionPart
    verbose_name = _('{} Bestandteil').format(Config.vocabulary('subscription'))
    verbose_name_plural = _('{} Bestandteile').format(Config.vocabulary('subscription'))
    extra = 0
