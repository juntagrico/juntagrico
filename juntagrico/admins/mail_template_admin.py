from juntagrico.admins import BaseAdmin
from juntagrico.config import Config


class MailTemplateAdmin(BaseAdmin):
    list_display = ['name']
    search_fields = ['name', 'template', 'code']

    def has_add_permission(self, request):
        if Config.unlock_mailtemplates():
            return super().has_add_permission(request)
        return False

    def get_readonly_fields(self, request, obj=None):
        if Config.unlock_mailtemplates():
            return super().get_readonly_fields(request, obj)
        return ['template', 'code']
