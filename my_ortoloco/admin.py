# -*- coding: utf-8 -*-
import datetime

from django.contrib import admin, messages
from django import forms
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.conf.urls import url
from django.utils import timezone
from django.core.urlresolvers import reverse

from my_ortoloco.models import *
from my_ortoloco import helpers
from my_ortoloco import admin_helpers

# This form exists to restrict primary user choice to users that have actually set the
# current abo as their abo
class AboAdminForm(forms.ModelForm):
    class Meta:
        model = Abo
        fields = '__all__'
        
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
        model = RecuringJob
        fields = ["typ", "slots"]

    weekdays = forms.MultipleChoiceField(label="Wochentage", choices=helpers.weekday_choices,
                                         widget=forms.widgets.CheckboxSelectMultiple)

    time = forms.TimeField(label="Zeit", required=False,
                           widget=admin.widgets.AdminTimeWidget)

    start_date = forms.DateField(label="Anfangsdatum", required=True,
                                 widget=admin.widgets.AdminDateWidget)
    end_date = forms.DateField(label="Enddatum", required=True,
                               widget=admin.widgets.AdminDateWidget)

    weekly = forms.ChoiceField(choices=[(7, "jede Woche"), (14, "Alle zwei Wochen")],
                               widget=forms.widgets.RadioSelect, initial=7)


    def __init__(self, *a, **k):
        super(JobCopyForm, self).__init__(*a, **k)
        inst = k.pop("instance")

        self.fields["start_date"].initial = inst.time.date() + datetime.timedelta(days=1)
        self.fields["time"].initial = inst.time
        self.fields["weekdays"].initial = [inst.time.isoweekday()]


    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        if "start_date" in cleaned_data and "end_date" in cleaned_data:
            if not self.get_dates(cleaned_data):
                raise ValidationError("Kein neuer Job fällt zwischen Anfangs- und Enddatum")
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
            job = RecuringJob.objects.create(typ=inst.typ, slots=inst.slots, time=dt)
            newjobs.append(job)
            job.save()

        # create new objects
        # HACK: admin expects a saveable object to be returned when commit=False
        #return newjobs[-1]
        return inst


    def save_m2m(self):
        # HACK: the admin expects this method to exist
        pass


    def get_dates(self, cleaned_data):
        start = cleaned_data["start_date"]
        end = cleaned_data["end_date"]
        weekdays = cleaned_data["weekdays"]
        weekdays = set(int(i) for i in weekdays)
        res = []
        skip_even_weeks = cleaned_data["weekly"] == "14"
        for delta in range((end - start).days + 1):
            if skip_even_weeks and delta % 14 >= 7:
                continue
            date = start + datetime.timedelta(delta)
            if not date.isoweekday() in weekdays:
                continue
            res.append(date)
        return res


class BoehnliInline(admin.TabularInline):
    model = Boehnli
    #readonly_fields = ["loco"]
    raw_id_fields = ["loco"]

    #can_delete = False

    # TODO: added these temporarily, need to be removed
    extra = 0
    max_num = 0


    def get_extra(self, request, obj=None):
        # TODO is this needed?
        #if "copy_job" in request.path:
        #    return 0
        if obj is None:
            return 0
        return obj.freie_plaetze()


    def get_max_num(self, request, obj):
        if obj is None:
            return 0
        return obj.slots


class JobAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "typ", "time", "slots", "freie_plaetze"]
    actions = ["copy_job", "mass_copy_job"]
    search_fields = ["typ__name", "typ__bereich__name"]
    exclude = ["reminder_sent"]
    inlines = [BoehnliInline]
    readonly_fields = ["freie_plaetze"]

    def mass_copy_job(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, u"Genau 1 Job auswählen!", level=messages.ERROR)
            return HttpResponseRedirect("")

        inst, = queryset.all()
        return HttpResponseRedirect("copy_job/%s/" % inst.id)

    mass_copy_job.short_description = "Job mehrfach kopieren..."


    def copy_job(self, request, queryset):
        for inst in queryset.all():
            newjob = RecuringJob(typ=inst.typ, slots=inst.slots, time=inst.time)
            newjob.save()

    copy_job.short_description = "Jobs kopieren"


    def get_form(self, request, obj=None, **kwds):
        if "copy_job" in request.path:
            return JobCopyForm
        return super(JobAdmin, self).get_form(request, obj, **kwds)


    def get_urls(self):
        urls = super(JobAdmin, self).get_urls()
        my_urls = [
                           url(r"^copy_job/(?P<jobid>.*?)/$", self.admin_site.admin_view(self.copy_job_view))
        ]
        return my_urls + urls


    def copy_job_view(self, request, jobid):
        # HUGE HACK: modify admin properties just for this view
        tmp_readonly = self.readonly_fields
        tmp_inlines = self.inlines
        self.readonly_fields = []
        self.inlines = []
        res = self.change_view(request, jobid, extra_context={'title': "Copy job"})
        self.readonly_fields = tmp_readonly
        self.inlines = tmp_inlines
        return res
    
    def get_queryset(self, request):
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if  request.user.has_perm("my_ortoloco.is_area_admin") and (not (request.user.is_superuser or request.user.has_perm("my_ortoloco.is_operations_group"))):
            return qs.filter(typ__bereich__coordinator=request.user.loco)
	return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "typ" and request.user.has_perm("my_ortoloco.is_area_admin") and (not (request.user.is_superuser or request.user.has_perm("my_ortoloco.is_operations_group"))):
            kwargs["queryset"] = JobType.objects.filter(bereich__coordinator=request.user.loco)
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class OneTimeJobAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "time", "slots", "freie_plaetze"]
    actions = ["transform_job"]
    search_fields = ["name", "bereich__name"]
    exclude = ["reminder_sent"]
    
    inlines = [BoehnliInline]
    readonly_fields = ["freie_plaetze"]
    
    def transform_job(self, request, queryset):
        for inst in queryset.all():
            t = JobType()
            rj = RecuringJob()
            helpers.attribute_copy(inst,t)
            helpers.attribute_copy(inst,rj)
            name = t.name
            t.name="something temporal which possibly is never used"
            t.save()
            rj.typ=t
            rj.save()    
            for b in Boehnli.objects.filter(job_id=inst.id):
                b.job = rj
                b.save()
            inst.delete()
            t.name = name
            t.save()

    transform_job.short_description = "EinzelJobs in Jobart konvertieren"
    
    def get_queryset(self, request):
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if  request.user.has_perm("my_ortoloco.is_area_admin") and (not (request.user.is_superuser or request.user.has_perm("my_ortoloco.is_operations_group"))):
            return qs.filter(bereich__coordinator=request.user.loco)
	return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "bereich" and request.user.has_perm("my_ortoloco.is_area_admin") and (not (request.user.is_superuser or request.user.has_perm("my_ortoloco.is_operations_group"))):
            kwargs["queryset"] = Taetigkeitsbereich.objects.filter(coordinator=request.user.loco)
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class JobTypeAdmin(admin.ModelAdmin):
    list_display = ["__unicode__"]
    actions = ["transform_job_type"]
    
    def transform_job_type(self, request, queryset):
        for inst in queryset.all():
            i=0
            for rj in RecuringJob.objects.filter(typ_id = inst.id):
                oj = OneTimeJob()
                helpers.attribute_copy(inst,oj)
                helpers.attribute_copy(rj,oj)
                oj.name = oj.name + str(i)
                i = i+1
                print oj.__dict__
                oj.save()    
                for b in Boehnli.objects.filter(job_id=rj.id):
                    b.job = oj
                    b.save()
                rj.delete()
            inst.delete()

    transform_job_type.short_description = "Jobart in EinzelJobs konvertieren"
    
    def get_queryset(self, request):
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if  request.user.has_perm("my_ortoloco.is_area_admin") and (not (request.user.is_superuser or request.user.has_perm("my_ortoloco.is_operations_group"))):
            return qs.filter(bereich__coordinator=request.user.loco)
	return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "bereich" and request.user.has_perm("my_ortoloco.is_area_admin") and (not (request.user.is_superuser or request.user.has_perm("my_ortoloco.is_operations_group"))):
            kwargs["queryset"] = Taetigkeitsbereich.objects.filter(coordinator=request.user.loco)
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    
class AboAdmin(admin.ModelAdmin):
    form = AboAdminForm
    list_display = ["__unicode__", "bezieher", "primary_loco_nullsave", "depot", "active"]
    #filter_horizontal = ["users"]
    search_fields = ["locos__user__username", "locos__first_name", "locos__last_name", "depot__name"]
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
    list_display = ["name", "code", "weekday", "contact"]
    
    


class BereichAdmin(admin.ModelAdmin):
    filter_horizontal = ["locos"]
    raw_id_fields = ["coordinator"]
    list_display = ["name", "core", "hidden", "coordinator"]

    def get_queryset(self, request):
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if  request.user.has_perm("my_ortoloco.is_area_admin") and (not (request.user.is_superuser or request.user.has_perm("my_ortoloco.is_operations_group"))):
            return qs.filter(coordinator=request.user.loco)
	return qs

class BoehnliAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if  request.user.has_perm("my_ortoloco.is_area_admin") and (not (request.user.is_superuser or request.user.has_perm("my_ortoloco.is_operations_group"))):
            otjidlist= list(OneTimeJob.objects.filter(bereich__coordinator=request.user.loco).values_list('id', flat=True))
            rjidlist= list(RecuringJob.objects.filter(typ__bereich__coordinator=request.user.loco).values_list('id', flat=True))
            jidlist = otjidlist + rjidlist
            return qs.filter(job__id__in=jidlist)
	return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "job" and request.user.has_perm("my_ortoloco.is_area_admin") and (not (request.user.is_superuser or request.user.has_perm("my_ortoloco.is_operations_group"))):
            otjidlist= list(OneTimeJob.objects.filter(bereich__coordinator=request.user.loco).values_list('id', flat=True))
            rjidlist= list(RecuringJob.objects.filter(typ__bereich__coordinator=request.user.loco).values_list('id', flat=True))
            jidlist = otjidlist + rjidlist
            kwargs["queryset"] = Job.objects.filter(id__in=jidlist)
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

"""
class BoehnliAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "job", "zeit", "loco"]
    raw_id_fields = ["job", "loco"]
"""


class LocoAdminForm(forms.ModelForm):
    class Meta:
        model = Loco
        fields = '__all__'

    def __init__(self, *a, **k):
        forms.ModelForm.__init__(self, *a, **k)
        loco = k.get("instance")
        if loco is None:
            link = ""
        elif loco.abo:
            url = reverse("admin:my_ortoloco_abo_change", args=(loco.abo.id,))
            link = "<a href=%s>%s</a>" % (url, loco.abo)
        else:
            link = "Kein Abo"
        self.fields["abo_link"].initial = link

    abo_link = forms.URLField(widget=admin_helpers.MyHTMLWidget(), required=False,
                              label="Abo")


class LocoAdmin(admin.ModelAdmin):
    form = LocoAdminForm
    list_display = ["email", "first_name", "last_name"]
    search_fields = ["first_name", "last_name", "email"]
    #raw_id_fields = ["abo"]
    exclude = ["abo"]
    readonly_fields = ["user"]
    actions = ["impersonate_job"]


    def impersonate_job(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, u"Genau 1 Loco auswählen!", level=messages.ERROR)
            return HttpResponseRedirect("")
        inst, = queryset.all()
        return HttpResponseRedirect("/impersonate/%s/" % inst.user.id)

    impersonate_job.short_description = "Loco imitieren (impersonate)..."


admin.site.register(Depot, DepotAdmin)
admin.site.register(ExtraAbo)
admin.site.register(ExtraAboType)
admin.site.register(ExtraAboCategory)
admin.site.register(Boehnli,BoehnliAdmin)
admin.site.register(Abo, AboAdmin)
admin.site.register(Loco, LocoAdmin)
admin.site.register(Taetigkeitsbereich, BereichAdmin)
admin.site.register(Anteilschein, AnteilscheinAdmin)
admin.site.register(MailTemplate)

# This is only added to admin for debugging
#admin.site.register(model_audit.Audit, AuditAdmin)

# Not adding this because it can and should be edited from Job, 
# where integrity constraints are checked
#admin.site.register(Boehnli, BoehnliAdmin)
admin.site.register(JobType, JobTypeAdmin)
admin.site.register(RecuringJob, JobAdmin)
admin.site.register(OneTimeJob, OneTimeJobAdmin)
