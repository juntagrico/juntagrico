from juntagrico.admins import BaseAdmin
from adminsortable2.admin import SortableAdminMixin


class DepotAdmin(SortableAdminMixin, BaseAdmin):
    raw_id_fields = ['contact']
    list_display = ['name', 'weekday', 'contact', 'visible', 'depot_list']

