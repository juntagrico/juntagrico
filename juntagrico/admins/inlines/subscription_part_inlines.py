from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity.subs import SubscriptionPart


class SubscriptionPartInlineFormset(BaseInlineFormSet):
    def clean(self):
        required_shares = 0
        future_parts_count = 0
        for form in self.forms:
            if form.instance.cancellation_date is None and not form.cleaned_data.get('DELETE', False) \
                    and form.cleaned_data.get('type') is not None:
                required_shares += form.instance.type.shares
                future_parts_count += 1 if form.instance.cancellation_date is None else 0
        available_shares = sum([member.usable_shares_count for member in self.instance.future_members])
        if required_shares > available_shares:
            raise ValidationError(
                _('Nicht genug {0} vorhanden. Vorhanden {1}. Benötigt {2}').format(Config.vocabulary('share_pl'),
                                                                                   available_shares,
                                                                                   required_shares),
                code='invalid')
        if future_parts_count == 0 and self.instance.cancellation_date is None:
            raise ValidationError(
                _('Nicht gekündigte {0} brauchen mindestens einen aktiven oder wartenden {0}-Bestandteil.'
                  ' Um die Kündigung rückgängig zu machen, leere und speichere zuerst das Kündigungsdatum des Bestandteils und dann jenes vom {0}.').format(
                    Config.vocabulary('subscription')))


class SubscriptionPartInline(admin.TabularInline):
    formset = SubscriptionPartInlineFormset
    model = SubscriptionPart
    verbose_name = _('{} Bestandteil').format(Config.vocabulary('subscription'))
    verbose_name_plural = _('{} Bestandteile').format(Config.vocabulary('subscription'))
    extra = 0
