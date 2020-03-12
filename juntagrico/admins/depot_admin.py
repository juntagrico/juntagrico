from juntagrico.admins import BaseAdmin


class DepotAdmin(BaseAdmin):
    raw_id_fields = ['contact']
    list_display = ['name', 'code', 'weekday', 'contact']
