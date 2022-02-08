from adminsortable2.admin import SortableAdminMixin

from juntagrico.admins import RichTextAdmin


class DepotAdmin(SortableAdminMixin, RichTextAdmin):
    raw_id_fields = ['contact']
    list_display = ['name', 'weekday', 'contact', 'visible', 'depot_list']
    exclude = ['capacity']
