import datetime

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity.member import SubscriptionMembership


class SubscriptionMembershipInlineFormset(BaseInlineFormSet):
    def clean(self):
        def consider_form(form):
            leave_date = getattr(form.instance, 'leave_date', None)
            return not form.cleaned_data.get('DELETE', False) \
                and (leave_date is None or leave_date > datetime.date.today()) \
                and hasattr(form.instance, 'member')
        if not self.instance.inactive:
            members = [form.instance.member for form in self.forms if consider_form(form)]
        else:
            members = [form.instance.member for form in self.forms]
        self.instance.override_future_members = set(members)
        if not members:
            raise ValidationError(_('Mindestens eine Mitgliedschaft wird benötigt.'),
                                  code='require_subscription_membership')
        if self.instance.primary_member not in members:
            self.instance.primary_member = members[0] if len(members) > 0 else None


class SubscriptionMembershipInline(admin.TabularInline):
    model = SubscriptionMembership
    fields = ['member', 'subscription', 'join_date', 'leave_date']
    autocomplete_fields = ['member', 'subscription']
    ordering = ['join_date']

    verbose_name = _('{} Mitgliedschaft').format(Config.vocabulary('subscription'))
    verbose_name_plural = _('{} Mitgliedschaften').format(Config.vocabulary('subscription'))
    extra = 0


class SubscriptionMembershipInlineWithShareCount(SubscriptionMembershipInline):
    formset = SubscriptionMembershipInlineFormset
    fields = SubscriptionMembershipInline.fields + ['share_count']
    readonly_fields = ['share_count']

    @admin.display(description=_('Verwendbare {}').format(Config.vocabulary('share_pl')))
    def share_count(self, instance):
        return instance.member.usable_shares_count
