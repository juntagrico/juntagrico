from django.contrib import admin
from loco_app.models import *


#Admins can have
#   list_filter 
#   filter_horizontal for manytomanyfields

class EndFilter(admin.SimpleListFilter):
    title = "aktuell"
    parameter_name = "endnull"

    def lookups(self, request, model_admin):
        return (('1', 'Ja'),
                ('0', 'Nein'))

    def queryset(self, request, queryset):
        if self.value() == "0":
            return queryset.filter(end__isnull=False)
        if self.value() == "1":
            return queryset.filter(end__isnull=True)
        return queryset

class AboHistoryAdmin(admin.ModelAdmin):
    list_display = ["abo_id", "user", "start", "end"]
    list_filter = [EndFilter]
    search_fields = ["user__username", "user__first_name", "user__last_name", "abo__id"]

    def abo_id(self, ah):
        return ah.abo.id


class AboHistoryInline(admin.TabularInline):
    model = AboHistory
    can_delete = False
    readonly_fields = ["abo", "user", "start"]

    def get_queryset(self, request):
        print "asdasdasd"
        qs = admin.TabularInline.get_queryset(self, request)
        return qs.filter(end=None)

    
class AboAdmin(admin.ModelAdmin):
    inlines = [AboHistoryInline]


admin.site.register(Depot)
admin.site.register(AboType)
admin.site.register(ExtraAboType)
admin.site.register(Abo, AboAdmin)
admin.site.register(Loco)
admin.site.register(AboHistory, AboHistoryAdmin)
