from django.contrib import admin
from django import forms
from my_ortoloco.models import *
from django.db.models import Q


# This form exists to restrict primary user choice to users that have actually set the
# current abo as their abo
class AboAdminForm(forms.ModelForm):
    class Meta:
        model = Abo

    abo_locos = forms.ModelMultipleChoiceField(queryset=Loco.objects.all(), required=False,
                                               widget=admin.widgets.FilteredSelectMultiple("Locos", False))

    def __init__(self, *a, **k):
        forms.ModelForm.__init__(self, *a, **k)
        self.fields["primary_loco"].queryset = Loco.objects.filter(abo=self.instance)
        self.fields["abo_locos"].queryset = Loco.objects.filter(Q(abo=None) | Q(abo=self.instance))
        self.fields["abo_locos"].initial = Loco.objects.filter(abo=self.instance)


    def clean(self):
        # enforce integrity constraint on primary_loco
        locos = self.cleaned_data["abo_locos"]
        primary = self.cleaned_data["primary_loco"]
        if len(locos) == 0:
            self.cleaned_data["primary_loco"] = None
        elif primary not in locos:
            self.cleaned_data["primary_loco"] = locos[0]

        return forms.ModelForm.clean(self)
        

    def save(self, commit=True):
        if self.instance:
            # update Abo-Loco many-to-one through foreign keys on Locos
            old_locos = set(Loco.objects.filter(abo=self.instance))
            new_locos = set(self.cleaned_data["abo_locos"])
            for obj in old_locos - new_locos:
                obj.abo = None
                obj.save()
            for obj in new_locos - old_locos:
                obj.abo = self.instance
                obj.save()

        return forms.ModelForm.save(self, commit)


class AboAdmin(admin.ModelAdmin):
    form = AboAdminForm
    list_display = ["__unicode__", "bezieher", "verantwortlicher_bezieher"]
    #filter_horizontal = ["users"]
    search_fields = ["locos__user__username", "locos__user__first_name", "locos__user__last_name"]


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


class BoehnliAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "job", "zeit", "loco"]


admin.site.register(Depot)
admin.site.register(StaticContent)
admin.site.register(Media)
admin.site.register(Download)
admin.site.register(Link)
admin.site.register(ExtraAboType)
admin.site.register(Abo, AboAdmin)
admin.site.register(Loco)
admin.site.register(Politoloco)
admin.site.register(Taetigkeitsbereich, BereichAdmin)
admin.site.register(Anteilschein, AnteilscheinAdmin)
admin.site.register(model_audit.Audit, AuditAdmin)

admin.site.register(Boehnli, BoehnliAdmin)
admin.site.register(JobTyp)
admin.site.register(Job)

