from juntagrico.admins import BaseAdmin
from juntagrico.admins.forms.subscription_admin_form import SubscriptionAdminForm
from juntagrico.admins.inlines.extra_subscription_inline import ExtraSubscriptionInline
from juntagrico.admins.inlines.subscription_type_inlines import FutureSubscriptionTypeInline
from juntagrico.admins.inlines.subscription_type_inlines import SubscriptionTypeInline


class SubscriptionAdmin(BaseAdmin):
    form = SubscriptionAdminForm
    list_display = ['__str__', 'recipients_names',
                    'primary_member_nullsave', 'depot', 'active']
    search_fields = ['members__user__username', 'members__first_name', 'members__last_name',
                     'members_future__user__username', 'members_future__first_name', 'members_future__last_name',
                     'members_old__user__username', 'members_old__first_name', 'members_old__last_name',
                     'depot__name']
    inlines = [SubscriptionTypeInline,
               FutureSubscriptionTypeInline, ExtraSubscriptionInline]
