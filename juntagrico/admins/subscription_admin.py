from django.contrib import admin

from juntagrico.admins.forms.subscription_admin_form import SubscriptionAdminForm
from juntagrico.admins.inlines.extra_subscription_inline import ExtraSubscriptionInline
from juntagrico.admins.inlines.future_subscription_type_inline import FutureSubscriptionTypeInline
from juntagrico.admins.inlines.subscription_type_inline import SubscriptionTypeInline
from juntagrico.util.addons import get_subscription_inlines


class SubscriptionAdmin(admin.ModelAdmin):
    form = SubscriptionAdminForm
    list_display = ['__str__', 'recipients_names',
                    'primary_member_nullsave', 'depot', 'active']
    search_fields = ['members__user__username',
                     'members__first_name', 'members__last_name', 'depot__name']
    inlines = [SubscriptionTypeInline,
               FutureSubscriptionTypeInline, ExtraSubscriptionInline]

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_subscription_inlines())
        super(SubscriptionAdmin, self).__init__(*args, **kwargs)
