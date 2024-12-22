from adminsortable2.admin import SortableAdminMixin

from juntagrico.admins import RichTextAdmin


class SubscriptionProductAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']
