from django.forms import BaseInlineFormSet

from juntagrico.admins.forms.subscriptionmembership_admin_form import SubscriptionMembershipAdminForm
from juntagrico.dao.memberdao import MemberDao

from django.contrib import admin
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity.member import SubscriptionMembership


class SubscriptionMembershipInlineFormset(BaseInlineFormSet):
    def clean(self):
        def consider_form(form):
            return not form.cleaned_data.get('DELETE', False) \
                   and (hasattr(form.instance, 'leave_date') and form.instance.leave_date is None) \
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
    form = SubscriptionMembershipAdminForm
    formset = SubscriptionMembershipInlineFormset
    fields = ['member', 'join_date', 'leave_date', 'share_count']
    readonly_fields = ['share_count']
    verbose_name = _('{} Mitgliedschaft').format(Config.vocabulary('subscription'))
    verbose_name_plural = _('{} Mitgliedschaften').format(Config.vocabulary('subscription'))
    extra = 0

    def share_count(self, instance):
        return instance.member.usable_shares_count
    share_count.short_description = Config.vocabulary('share_pl')

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(SubscriptionMembershipInline, self).get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'member':
            if self.parent_obj is None:
                kwargs['queryset'] = MemberDao.members_for_create_subscription()
            elif self.parent_obj.state == 'waiting':
                kwargs['queryset'] = MemberDao.members_for_future_subscription(self.parent_obj)
            elif self.parent_obj.state == 'inactive':
                kwargs['queryset'] = MemberDao.all_members()
            else:
                kwargs['queryset'] = MemberDao.members_for_subscription(self.parent_obj)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
