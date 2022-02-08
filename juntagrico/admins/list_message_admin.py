from adminsortable2.admin import SortableAdminMixin

from juntagrico.admins import BaseAdmin


class ListMessageAdmin(SortableAdminMixin, BaseAdmin):
    list_display = ['message', 'active']
    search_fields = ['message']
