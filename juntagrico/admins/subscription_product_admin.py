from adminsortable2.admin import SortableAdminMixin, SortableTabularInline

from juntagrico.admins import RichTextAdmin
from juntagrico.entity.subtypes import ProductSize


class ProductSizeInline(SortableTabularInline):
    model = ProductSize
    fields = ['name', 'product', 'units', 'show_on_depot_list']
    extra = 0


class SubscriptionProductAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']
    inlines = [ProductSizeInline]
