from django.contrib import admin

from juntagrico.entity.extrasubs import ExtraSubscription


class ExtraSubscriptionInline(admin.TabularInline):
    model = ExtraSubscription
    fk_name = 'main_subscription'

    def get_extra(self, request, obj=None, **kwargs):
        return 0
