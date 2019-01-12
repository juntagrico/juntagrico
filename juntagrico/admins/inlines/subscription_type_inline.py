from django.contrib import admin

from juntagrico.entity.subs import Subscription


class SubscriptionTypeInline(admin.TabularInline):
    model = Subscription.types.through
    verbose_name = 'Abo Typ'
    verbose_name_plural = 'Abo Typen'
    extra = 0
