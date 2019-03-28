from django.contrib import admin

from juntagrico.config import Config
from juntagrico.util.addons import get_subtype_inlines


class SubscriptionTypeAdmin(admin.ModelAdmin):
    inlines = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_subtype_inlines())
        super(SubscriptionTypeAdmin, self).__init__(*args, **kwargs)

    def get_exclude(self, request, obj=None):
        if not Config.enable_shares():
            return ['shares'] if self.exclude is None else self.exclude.append('shares')
        return self.exclude
