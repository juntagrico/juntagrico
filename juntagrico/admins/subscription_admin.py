from django.utils.translation import gettext as _

from juntagrico.admins import BaseAdmin
from juntagrico.admins.forms.subscription_admin_form import SubscriptionAdminForm
from juntagrico.admins.inlines.subscription_membership_inlines import SubscriptionMembershipInline
from juntagrico.admins.inlines.subscription_part_inlines import SubscriptionPartInline
from juntagrico.config import Config


class SubscriptionAdmin(BaseAdmin):
    form = SubscriptionAdminForm
    readonly_fields = ('creation_date',)
    list_display = ['__str__', 'recipients_names',
                    'primary_member_nullsave', 'depot', 'text_state']
    search_fields = ['subscriptionmembership__member__user__username',
                     'subscriptionmembership__member__first_name',
                     'subscriptionmembership__member__last_name',
                     'depot__name', 'nickname']

    inlines = [SubscriptionMembershipInline, SubscriptionPartInline]

    fieldsets = [
        (Config.vocabulary('member_pl'), {'fields': ['primary_member', 'nickname']}),
        (Config.vocabulary('depot'), {'fields': ['depot', 'future_depot']}),
        (_('Status'), {'fields': ['creation_date', 'start_date', 'activation_date',
                                  'cancellation_date', 'end_date', 'deactivation_date']}),
        (_('Administration'), {'fields': ['notes']}),
    ]
    add_fieldsets = [
        (Config.vocabulary('depot'), {'fields': ['depot']}),
        (_('Status'), {'fields': ['creation_date', 'start_date', 'activation_date',
                                  'cancellation_date', 'end_date', 'deactivation_date']}),
        (_('Administration'), {'fields': ['notes']}),
    ]

    def text_state(self, instance):
        return instance.state_text

    text_state.short_description = _('Status')
    text_state.admin_order_field = 'activation_date'

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        sub_is_deactivated = obj.inactive
        if sub_is_deactivated and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.can_change_deactivated_subscriptions'))):
            for inline in self.inlines:
                readonly_fields = inline.readonly_fields or []
                readonly_fields.extend([field.name for field in inline.model._meta.fields])
                inline.readonly_fields = list(set(readonly_fields))
            return [field.name for field in obj._meta.fields]
        return self.readonly_fields
