from django.contrib import admin

from juntagrico.util.addons import get_subsize_inlines


class SubscriptionSizeAdmin(admin.ModelAdmin):
    inlines = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_subsize_inlines())
        super(SubscriptionSizeAdmin, self).__init__(*args, **kwargs)
