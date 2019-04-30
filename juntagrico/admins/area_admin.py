from django.contrib import admin

from juntagrico.util.addons import get_area_inlines
from juntagrico.util.admin import queryset_for_coordinator


class AreaAdmin(admin.ModelAdmin):
    filter_horizontal = ['members']
    raw_id_fields = ['coordinator']
    list_display = ['name', 'core', 'hidden', 'coordinator']
    inlines = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_area_inlines())
        super(AreaAdmin, self).__init__(*args, **kwargs)

    def get_queryset(self, request):
        return queryset_for_coordinator(self, request, 'coordinator')

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            return ['name', 'core', 'hidden', 'coordinator']
        return self.readonly_fields
