from django.contrib import admin

from juntagrico.entity.subs import SubscriptionPart


class ExtraSubscriptionInline(admin.TabularInline):
    model = SubscriptionPart
    fk_name = 'subscription'

    def get_extra(self, request, obj=None, **kwargs):
        return 0
