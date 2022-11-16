from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity.member import SubscriptionMembership


class SubscriptionMembershipInlineFormset(BaseInlineFormSet):
    def clean(self):
        def consider_form(form):
            leave_date = getattr(form.instance, 'leave_date', None)
            return not form.cleaned_data.get('DELETE', False) \
                and (leave_date is None or leave_date > timezone.now().date()) \
                and hasattr(form.instance, 'member')
        if not self.instance.inactive:
            members = [form.instance.member for form in self.forms if consider_form(form)]
        else:
            members = [form.instance.member for form in self.forms]
        self.instance.override_future_members = set(members)
        if self.instance.primary_member not in members:
            self.instance.primary_member = members[0] if len(members) > 0 else None


class SubscriptionMembershipInline(admin.TabularInline):
    model = SubscriptionMembership
    formset = SubscriptionMembershipInlineFormset
    fields = ['member', 'join_date', 'leave_date', 'share_count']
    raw_id_fields = ['member']
    readonly_fields = ['share_count']
    verbose_name = _('{} Mitgliedschaft').format(Config.vocabulary('subscription'))
    verbose_name_plural = _('{} Mitgliedschaften').format(Config.vocabulary('subscription'))
    extra = 0

    @admin.display(description=_('Verwendbare {}').format(Config.vocabulary('share_pl')))
    def share_count(self, instance):
        return instance.member.usable_shares_count
