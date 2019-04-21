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
