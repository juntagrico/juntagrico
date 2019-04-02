from django.contrib import admin

from juntagrico.util.addons import get_subproduct_inlines


class SubscriptionProductAdmin(admin.ModelAdmin):
    inlines = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_subproduct_inlines())
        super(SubscriptionProductAdmin, self).__init__(*args, **kwargs)
