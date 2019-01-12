from django.contrib import admin

from juntagrico.util.addons import get_extrasub_inlines


class ExtraSubscriptionAdmin(admin.ModelAdmin):
    raw_id_fields = ['main_subscription']
    inlines = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_extrasub_inlines())
        super(ExtraSubscriptionAdmin, self).__init__(*args, **kwargs)
