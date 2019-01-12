from django.contrib import admin

from juntagrico.entity.subs import Subscription


class FutureSubscriptionTypeInline(admin.TabularInline):
    model = Subscription.future_types.through
    verbose_name = 'Zukunft Abo Typ'
    verbose_name_plural = 'Zukunft Abo Typen'
    extra = 0