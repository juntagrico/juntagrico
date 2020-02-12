from django.contrib.admin import register
from juntagrico.admins.base_admin import BaseAdmin
from juntagrico.entity.depot import Depot


@register(Depot)
class DepotAdmin(BaseAdmin):
    raw_id_fields = ['contact']
    list_display = ['name', 'code', 'weekday', 'contact']
