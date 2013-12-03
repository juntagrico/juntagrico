# -*- coding: utf-8 -*-
import datetime

from django.contrib import admin, messages
from django import forms
from django.db.models import Q
from django.http import  HttpResponse, HttpResponseRedirect
from django.conf.urls import patterns
from django.utils import timezone

from my_ortoloco.models import *
from my_ortoloco import helpers


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
        if primary not in locos:
            self.cleaned_data["primary_loco"] = locos[0] if locos else None

        return forms.ModelForm.clean(self)
        

    def save(self, commit=True):
        # HACK: set commit=True, ignoring what the admin tells us.
        # This causes save_m2m to be called.
        return forms.ModelForm.save(self, commit=True)


    def save_m2m(self):
        # update Abo-Loco many-to-one through foreign keys on Locos
        old_locos = set(Loco.objects.filter(abo=self.instance))
        new_locos = set(self.cleaned_data["abo_locos"])
        for obj in old_locos - new_locos:
            obj.abo = None
            obj.save()
        for obj in new_locos - old_locos:
            obj.abo = self.instance
            obj.save()


class JobCopyForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["typ", "slots", "earning"]

    weekdays = forms.MultipleChoiceField(label="Wochentage", choices=helpers.weekday_choices, 
                                         widget=forms.widgets.CheckboxSelectMultiple)

    time = forms.TimeField(label="Zeit", required=False,
                           widget=admin.widgets.AdminTimeWidget)

    start_date = forms.DateField(label="Anfangsdatum", required=False,
                                 widget=admin.widgets.AdminDateWidget)
    end_date = forms.DateField(label="Enddatum", required=False,
                               widget=admin.widgets.AdminDateWidget)

    
    def __init__(self, *a, **k):
        super(JobCopyForm, self).__init__(*a, **k)
        inst = k.pop("instance")

        self.fields["start_date"].initial = inst.time.date() + datetime.timedelta(days=1)
        self.fields["time"].initial = timezone.localtime(inst.time).timetz()
        self.fields["weekdays"].initial = [inst.time.weekday()]
    
    
    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        if not self.get_dates(cleaned_data):
            raise ValidationError("Not enough events")
        return cleaned_data
    

    def save(self, commit=True):
        weekdays = self.cleaned_data["weekdays"]
        start = self.cleaned_data["start_date"]
        end = self.cleaned_data["end_date"]
        time = self.cleaned_data["time"]

        inst = self.instance

        newjobs = []
        for date in self.get_dates(self.cleaned_data):
            dt = datetime.datetime.combine(date, time)
            job = Job.objects.create(typ=inst.typ, slots=inst.slots, time=dt, earning=inst.earning)
            newjobs.append(job)
            job.save()

        # create new objects
        # HACK: admin expects a saveable object to be returned when commit=False
        return newjobs[-1]


    def save_m2m(self):
        # HACK: the admin expects this method to exist
        pass


    def get_dates(self, cleaned_data):
        start = cleaned_data["start_date"]
        end = cleaned_data["end_date"]
        weekdays = cleaned_data["weekdays"]
        weekdays = set(int(i) for i in weekdays)
        res = []
        for delta in range((end - start).days + 1):
            date = start + datetime.timedelta(delta)
            if not date.weekday() in weekdays:
                continue
            res.append(date)
        return res


class BoehnliInline(admin.TabularInline):
    model = Boehnli
    #readonly_fields = ["loco"]
    raw_id_fields = ["loco"]

    #can_delete = False
    #extra = 0

   
    def get_extra(self, request, obj=None):
        if obj is None:
            return 0
        return obj.freie_plaetze()
    

    def get_max_num(self, request, obj):
        if obj is None:
            return 0
        return obj.slots


class JobAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "typ", "time", "earning", "slots", "freie_plaetze"]
    actions = ["copy_job"]
    inlines = [BoehnliInline]
    readonly_fields = ["freie_plaetze"]

    fieldsets = (
        (None, {"fields": ("typ",
                           "time", 
                           "earning",
                           "slots", 
                           "freie_plaetze")}),
    )



    def copy_job(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, u"Genau 1 Job auswählen!", level=messages.ERROR) 
            return HttpResponseRedirect("")

        inst, = queryset.all()
        return HttpResponseRedirect("copy_job/%s/" % inst.id)
    copy_job.short_description = "Job kopieren"


    def get_form(self, request, obj=None, **kwds):
        if "copy_job" in request.path:
            return JobCopyForm
        return super(JobAdmin, self).get_form(request, obj, **kwds)
        
    
    def get_urls(self):
        urls = super(JobAdmin, self).get_urls()
        my_urls = patterns("",
            (r"^copy_job/(?P<jobid>.*?)/$", self.admin_site.admin_view(self.copy_job_view))
        )
        return my_urls + urls


    def copy_job_view(self, request, jobid):
        return self.change_view(request, jobid, extra_context={'title':"Copy job"})
    


class AboAdmin(admin.ModelAdmin):
    form = AboAdminForm
    list_display = ["__unicode__", "bezieher", "verantwortlicher_bezieher"]
    #filter_horizontal = ["users"]
    search_fields = ["locos__user__username", "locos__first_name", "locos__last_name"]
    #raw_id_fields = ["primary_loco"]


class AuditAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "source_type", "target_type", "field", "action", 
                    "source_object", "target_object"]
    #can_delete = False


class AnteilscheinAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "loco"]
    search_fields = ["id", "loco__username", "loco__first_name", "loco__last_name"]
    raw_id_fields = ["loco"]


class DepotAdmin(admin.ModelAdmin):
    raw_id_fields = ["contact"]


class BereichAdmin(admin.ModelAdmin):
    filter_horizontal = ["locos"]
    raw_id_fields = ["coordinator"]


class BoehnliAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "job", "zeit", "loco"]
    raw_id_fields = ["job", "loco"]



class LocoAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "email"]
    search_fields = ["first_name", "last_name", "email"]
    raw_id_fields = ["abo"]
    readonly_fields = ["user"]



admin.site.register(Depot, DepotAdmin)
admin.site.register(ExtraAboType)
admin.site.register(Abo, AboAdmin)
admin.site.register(Loco, LocoAdmin)
admin.site.register(Taetigkeitsbereich, BereichAdmin)
admin.site.register(Anteilschein, AnteilscheinAdmin)

# This is only added to admin for debugging
admin.site.register(model_audit.Audit, AuditAdmin)

# Not adding this because it can and should be edited from Job, 
# where integrity constraints are checked
#admin.site.register(Boehnli, BoehnliAdmin)
admin.site.register(JobTyp)
admin.site.register(Job, JobAdmin)


