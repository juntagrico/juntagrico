from django.contrib import admin
from loco_app.models import *


#Admins can have
#   list_filter 
#   filter_horizontal for manytomanyfields


class AboAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "bezieher"]
    filter_horizontal = ["users"]
    search_fields = ["id", "users__username", "users__first_name", "users__last_name"]


class HistoryAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "action", "source_type", "source_object", "target_type", "target_object"]
    readonly_fields = list_display
    #search_fields = ["id"]
    #can_delete = False


admin.site.register(Depot)
admin.site.register(StaticContent)
admin.site.register(Medias)
admin.site.register(Downloads)
admin.site.register(Links)
admin.site.register(AboType)
admin.site.register(ExtraAboType)
admin.site.register(Abo, AboAdmin)
admin.site.register(Loco)
admin.site.register(model_audit.Audit, HistoryAdmin)
admin.site.register(StaticString)

