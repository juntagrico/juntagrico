from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext as _

from juntagrico.entity.subs import Subscription
from juntagrico.config import Config


class SubscriptionTypeInlineFormset(BaseInlineFormSet):
    def clean(self):
        required_shares = 0
        for form in self.forms:
            required_shares += form.instance.type.shares
        available_shares = sum([member.active_shares_count for member in self.instance._future_members])
        if required_shares > available_shares:
            raise ValidationError(
                _('Nicht genug {0} vorhanden. Vorhanden {1}. Benötigt {2}').format(Config.vocabulary('share_pl'),
                                                                                   available_shares,
                                                                                   required_shares),
                code='invalid')


class SubscriptionTypeInline(admin.TabularInline):
    formset = SubscriptionTypeInlineFormset
    model = Subscription.types.through
    verbose_name = _('{0}-Typ').format(Config.vocabulary('subscription'))
    verbose_name_plural = _('{0}-Typen').format(Config.vocabulary('subscription'))
    extra = 0


class FutureSubscriptionTypeInline(admin.TabularInline):
    formset = SubscriptionTypeInlineFormset
    model = Subscription.future_types.through
    verbose_name = _('Zukunft {0}-Typ').format(Config.vocabulary('subscription'))
    verbose_name_plural = _('Zukunft {0}-Typen').format(Config.vocabulary('subscription'))
    extra = 0
