from django.utils.translation import gettext as _

from juntagrico.admins import BaseAdmin
from juntagrico.admins.forms.subscription_admin_form import SubscriptionAdminForm
from juntagrico.admins.inlines.extra_subscription_inline import ExtraSubscriptionInline
from juntagrico.admins.inlines.subscription_part_inlines import SubscriptionPartInline
from juntagrico.config import Config


class SubscriptionAdmin(BaseAdmin):
    form = SubscriptionAdminForm
    readonly_fields = ('creation_date',)
    list_display = ['__str__', 'recipients_names',
                    'primary_member_nullsave', 'depot', 'text_state']
    search_fields = ['members__user__username', 'members__first_name', 'members__last_name',
                     'members_future__user__username', 'members_future__first_name', 'members_future__last_name',
                     'members_old__user__username', 'members_old__first_name', 'members_old__last_name',
                     'depot__name', 'nickname']

    inlines = [SubscriptionPartInline, ExtraSubscriptionInline]
    add_inlines = [SubscriptionPartInline, ExtraSubscriptionInline]
    fieldsets = [
        (Config.vocabulary('member_pl'), {'fields': ['primary_member', 'subscription_members', 'nickname']}),
        (_('Depot'), {'fields': ['depot', 'future_depot']}),
        (_('Status'), {'fields': ['creation_date', 'start_date', 'activation_date',
                                  'cancellation_date', 'end_date', 'deactivation_date']}),
        (_('Administration'), {'fields': ['notes']}),
    ]
    add_fieldsets = [
        (Config.vocabulary('member_pl'), {'fields': ['subscription_members']}),
        (Config.vocabulary('depot'), {'fields': ['depot']}),
        (_('Status'), {'fields': ['start_date']}),
        (_('Administration'), {'fields': ['notes']}),
    ]

    def text_state(self, instance):
        """ this method is necessary to show icons in the list view
        """
        return instance.state_text

    text_state.short_description = _('Status')
    text_state.admin_order_field = 'activation_date'

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_inlines(self, request, obj):
        if not obj:
            return self.add_inlines
        return super().get_inlines(request, obj)
