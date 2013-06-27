from django.contrib import admin
from django import forms
from loco_app.models import *


# This form exists to restrict primary user choice to users that have actually set the
# current abo as their abo
class AboAdminForm(forms.ModelForm):
    class Meta:
        model = Abo

    def __init__(self, *a, **k):
        forms.ModelForm.__init__(self, *a, **k)
        self.fields["primary_user"].queryset = User.objects.filter(abo=self.instance)
        self.fields["users"].queryset = User.objects.filter(abo=None)


class AboAdmin(admin.ModelAdmin):
    form = AboAdminForm
    list_display = ["__unicode__", "primary_user", "bezieher"]
    filter_horizontal = ["users"]
    search_fields = ["users__username", "users__first_name", "users__last_name"]


class AuditAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "source_type", "target_type", "field", "action", 
                    "source_object", "target_object"]
    readonly_fields = list_display
    #can_delete = False


class AnteilscheinAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "user"]
    search_fields = ["id", "user__username", "user__first_name", "user__last_name"]



class BereichAdmin(admin.ModelAdmin):
    filter_horizontal = ["users"]


admin.site.register(Depot)
admin.site.register(ExtraAboType)
admin.site.register(Abo, AboAdmin)
#admin.site.register(Loco)
admin.site.register(Taetigkeitsbereich, BereichAdmin)
admin.site.register(Anteilschein, AnteilscheinAdmin)
admin.site.register(model_audit.Audit, AuditAdmin)

