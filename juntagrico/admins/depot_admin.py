from django.contrib import admin

from juntagrico.util.addons import get_depot_inlines


class DepotAdmin(admin.ModelAdmin):
    raw_id_fields = ['contact']
    list_display = ['name', 'code', 'weekday', 'contact']
    inlines = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_depot_inlines())
        super(DepotAdmin, self).__init__(*args, **kwargs)
