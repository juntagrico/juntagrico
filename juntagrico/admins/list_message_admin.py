from juntagrico.admins import BaseAdmin


class ListMessageAdmin(BaseAdmin):
    list_display = ['message', 'active']
    search_fields = ['message']
