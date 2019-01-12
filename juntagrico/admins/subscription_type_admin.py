from django.contrib import admin

class SubscriptionTypeAdmin(admin.ModelAdmin):
    inlines = []

    def __init__(self, *args, **kwargs):
        from juntagrico.util.addons import get_subtype_inlines
        self.inlines.extend(get_subtype_inlines())
        super(SubscriptionTypeAdmin, self).__init__(*args, **kwargs)
