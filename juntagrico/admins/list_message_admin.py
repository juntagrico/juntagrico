from django.contrib.admin import register
from juntagrico.admins.base_admin import BaseAdmin
from juntagrico.entity.listmessage import ListMessage


@register(ListMessage)
class ListMessageAdmin(BaseAdmin):
    list_display = ['message', 'active']
    search_fields = ['message']
