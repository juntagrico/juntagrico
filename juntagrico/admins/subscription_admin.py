from django.contrib import admin
from django.utils.translation import gettext as _

from juntagrico.admins import BaseAdmin, DateRangeExportMixin
from juntagrico.admins.filters import SimpleStateModelFilter
from juntagrico.admins.forms.subscription_admin_form import SubscriptionAdminForm
from juntagrico.admins.inlines.subscription_membership_inlines import SubscriptionMembershipInlineWithShareCount
from juntagrico.admins.inlines.subscription_part_inlines import SubscriptionPartInline
from juntagrico.config import Config
from juntagrico.resources.subscription import SubscriptionResource, SubscriptionPartResource


class SubscriptionAdmin(DateRangeExportMixin, BaseAdmin):
    form = SubscriptionAdminForm
    readonly_fields = ('creation_date',)
    list_display = ['__str__', 'recipients_names',
                    'primary_member_nullsave', 'depot', 'text_state', 'cancellation_date']
    list_filter = (SimpleStateModelFilter, 'cancellation_date', ('depot', admin.RelatedOnlyFieldListFilter))
    search_fields = ['subscriptionmembership__member__user__username',
                     'subscriptionmembership__member__first_name',
                     'subscriptionmembership__member__last_name',
                     'depot__name', 'nickname', 'id']
    autocomplete_fields = ['depot', 'future_depot']

    inlines = [SubscriptionMembershipInlineWithShareCount, SubscriptionPartInline]

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

    resource_classes = [SubscriptionResource, SubscriptionPartResource]

    @admin.display(description=_('Status'), ordering='activation_date')
    def text_state(self, instance):
        return instance.state_text

    @admin.display(description='{}-BezieherInnen'.format(Config.vocabulary('subscription')))
    def recipients_names(self, instance):
        members = instance.current_members.order_by('first_name', 'last_name')
        return ', '.join(str(m) for m in members)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    @staticmethod
    def can_change_deactivated_subscription(request, obj=None):
        return obj is None or not obj.inactive or (
            request.user.is_superuser or request.user.has_perm('juntagrico.can_change_deactivated_subscriptions'))

    def has_change_permission(self, request, obj=None):
        return self.can_change_deactivated_subscription(request, obj) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.can_change_deactivated_subscription(request, obj) and super().has_delete_permission(request, obj)
