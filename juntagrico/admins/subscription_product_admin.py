from adminsortable2.admin import SortableAdminMixin

from juntagrico.admins import RichTextAdmin


class SubscriptionProductAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['name', 'is_extra']
    search_fields = ['name']
