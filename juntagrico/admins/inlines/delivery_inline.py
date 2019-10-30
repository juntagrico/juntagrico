from django.contrib import admin

from juntagrico.entity.delivery import DeliveryItem


class DeliveryInline(admin.TabularInline):
    model = DeliveryItem
