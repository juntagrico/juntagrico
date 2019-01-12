from django.contrib import admin

from juntagrico.util.addons import get_extrasubcat_inlines


class ExtraSubscriptionCategoryAdmin(admin.ModelAdmin):
    inlines = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_extrasubcat_inlines())
        super(ExtraSubscriptionCategoryAdmin, self).__init__(*args, **kwargs)
