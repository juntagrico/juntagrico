from django.contrib.admin import register
from juntagrico.admins.base_admin import BaseAdmin
from juntagrico.admins.inlines.delivery_inline import DeliveryInline
from juntagrico.entity.delivery import Delivery


@register(Delivery)
class DeliveryAdmin(BaseAdmin):
    list_display = ("__str__", "delivery_date", "subscription_size")
    ordering = ("-delivery_date", "subscription_size")
    actions = ["copy_delivery"]
    search_fields = ["delivery_date", "subscription_size"]
    inlines = [DeliveryInline]
    save_as = True
