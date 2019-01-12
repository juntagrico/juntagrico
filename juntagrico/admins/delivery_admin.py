from django.contrib import admin

from juntagrico.admins.inlines.delivery_inline import DeliveryInline
from juntagrico.util.addons import get_delivery_inlines


class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "delivery_date", "subscription_size")
    ordering = ("-delivery_date", "subscription_size")
    actions = ["copy_delivery"]
    search_fields = ["delivery_date", "subscription_size"]
    inlines = [DeliveryInline]
    save_as = True

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_delivery_inlines())
        super(DeliveryAdmin, self).__init__(*args, **kwargs)
