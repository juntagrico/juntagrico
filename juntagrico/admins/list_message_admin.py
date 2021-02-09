from juntagrico.admins import BaseAdmin
from adminsortable2.admin import SortableAdminMixin


class ListMessageAdmin(SortableAdminMixin, BaseAdmin):
    list_display = ['message', 'active']
    search_fields = ['message']
