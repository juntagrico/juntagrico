from adminsortable2.admin import SortableAdminMixin
from django.contrib.admin import TabularInline

from juntagrico.admins import RichTextAdmin
from juntagrico.entity.subtypes import ProductSize


class ProductSizeInline(TabularInline):
    model = ProductSize
    fields = ['name', 'product', 'units', 'show_on_depot_list']
    extra = 0


class SubscriptionProductAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']
    inlines = [ProductSizeInline]
