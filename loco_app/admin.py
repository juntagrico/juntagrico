from django.contrib import admin
from loco_app.models import *


#Admins can have
#   list_filter 
#   filter_horizontal for manytomanyfields


class AboAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "bezieher"]
    filter_horizontal = ["users"]
    search_fields = ["id", "users__username", "users__first_name", "users__last_name"]


class AuditAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "source_type", "target_type", "field", "action", "source_object", "target_object"]
    readonly_fields = list_display
    #can_delete = False


class BereichAdmin(admin.ModelAdmin):
    filter_horizontal = ["users"]


admin.site.register(Depot)
admin.site.register(AboType)
admin.site.register(ExtraAboType)
admin.site.register(Abo, AboAdmin)
#admin.site.register(Loco)
admin.site.register(Taetigkeitsbereich, BereichAdmin)
admin.site.register(Anteilschein)
admin.site.register(model_audit.Audit, AuditAdmin)
admin.site.register(StaticString)

