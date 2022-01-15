from juntagrico.admins import BaseAdmin


class TextOverrideAdmin(BaseAdmin):
    list_display = ['name']
    fields = ['name', 'text']

    def get_fields(self, request, obj=None):
        """ on object creation only text to override can be selected.
        """
        if not obj:
            return ['name']
        return super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """ text selection can not be changed once the object is created.
        """
        if obj:
            return ['name']
        return super().get_readonly_fields(request, obj)
