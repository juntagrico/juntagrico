from django.contrib import admin

from juntagrico.config import Config
from juntagrico.util.addons import get_extrasubtype_inlines


class ExtraSubscriptionTypeAdmin(admin.ModelAdmin):
    inlines = []
    exclude = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_extrasubtype_inlines())
        super(ExtraSubscriptionTypeAdmin, self).__init__(*args, **kwargs)
        if not Config.enable_shares():
            self.exclude.append('shares')
