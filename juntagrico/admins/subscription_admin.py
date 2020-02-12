from django.utils.translation import gettext as _
from django.contrib.admin import register

from juntagrico.admins.base_admin import BaseAdmin
from juntagrico.admins.forms.subscription_admin_form import SubscriptionAdminForm
from juntagrico.admins.inlines.extra_subscription_inline import ExtraSubscriptionInline
from juntagrico.admins.inlines.subscription_type_inlines import FutureSubscriptionTypeInline
from juntagrico.admins.inlines.subscription_type_inlines import SubscriptionTypeInline
from juntagrico.entity.subs import Subscription
from juntagrico.config import Config


@register(Subscription)
class SubscriptionAdmin(BaseAdmin):
    form = SubscriptionAdminForm
    readonly_fields = ('creation_date',)
    list_display = ['__str__', 'recipients_names',
                    'primary_member_nullsave', 'depot', 'active']
    search_fields = ['members__user__username', 'members__first_name', 'members__last_name',
                     'members_future__user__username', 'members_future__first_name', 'members_future__last_name',
                     'members_old__user__username', 'members_old__first_name', 'members_old__last_name',
                     'depot__name']
    inlines = [SubscriptionTypeInline, FutureSubscriptionTypeInline, ExtraSubscriptionInline]
    add_inlines = [SubscriptionTypeInline, ExtraSubscriptionInline]
    fieldsets = [
        (Config.vocabulary('member_pl'), {'fields': ['primary_member', 'subscription_members']}),
        (_('Depot'), {'fields': ['depot', 'future_depot']}),
        (_('Status'), {'fields': ['creation_date', 'start_date', 'active', 'activation_date',
                'canceled', 'cancelation_date', 'end_date', 'deactivation_date']}),
        (_('Administration'), {'fields': ['notes']}),
    ]
    add_fieldsets = [
        (Config.vocabulary('member_pl'), {'fields': ['subscription_members']}),
        (_('Depot'), {'fields': ['depot']}),
        (_('Status'), {'fields': ['start_date']}),
        (_('Administration'), {'fields': ['notes']}),
    ]

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_inlines(self, request, obj):
        if not obj:
            return self.add_inlines
        return super().get_inlines(request, obj)