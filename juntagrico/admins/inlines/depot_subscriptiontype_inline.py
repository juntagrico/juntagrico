from django.contrib import admin

from juntagrico.entity.depot import DepotSubscriptionTypeCondition


class DepotSubscriptionTypeInline(admin.TabularInline):
    model = DepotSubscriptionTypeCondition
    extra = 0
