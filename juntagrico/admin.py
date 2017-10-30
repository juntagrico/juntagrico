# -*- coding: utf-8 -*-


from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from juntagrico.config import Config
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.dao.jobdao import JobDao
from juntagrico.dao.jobtypedao import JobTypeDao
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.memberdao import MemberDao
from juntagrico.models import *
from juntagrico.util import admin as admin_util
from juntagrico.util.models import *
from juntagrico.util.temporal import *


# This form exists to restrict primary user choice to users that have actually set the
# current subscription as their subscription


class SubscriptionAdminForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = '__all__'

    subscription_members = forms.ModelMultipleChoiceField(queryset=MemberDao.all_members(), required=False,
                                                          widget=admin.widgets.FilteredSelectMultiple('Member', False))

    def __init__(self, *a, **k):
        forms.ModelForm.__init__(self, *a, **k)
        self.fields['primary_member'].queryset = self.instance.members.all()
        self.fields['subscription_members'].queryset = MemberDao.members_for_subscription(self.instance)
        self.fields['subscription_members'].initial = self.instance.members.all()

    def clean(self):
        # enforce integrity constraint on primary_member
        members = self.cleaned_data['subscription_members']
        primary = self.cleaned_data['primary_member']
        if primary not in members:
            self.cleaned_data['primary_member'] = members[0] if members else None

        return forms.ModelForm.clean(self)

    def save(self, commit=True):
        # HACK: set commit=True, ignoring what the admin tells us.
        # This causes save_m2m to be called.
        return forms.ModelForm.save(self, commit=True)

    def save_m2m(self):
        # update Subscription-Member many-to-one through foreign keys on Members
        old_members = set(self.instance.members.all())
        new_members = set(self.cleaned_data['subscription_members'])
        for obj in old_members - new_members:
            obj.subscription = None
            obj.save()
        for obj in new_members - old_members:
            obj.subscription = self.instance
            obj.save()


class JobCopyForm(forms.ModelForm):
    class Meta:
        model = RecuringJob
        fields = ['type', 'slots']

    weekdays = forms.MultipleChoiceField(label='Wochentage', choices=weekday_choices,
                                         widget=forms.widgets.CheckboxSelectMultiple)

    time = forms.TimeField(label='Zeit', required=False,
                           widget=admin.widgets.AdminTimeWidget)

    start_date = forms.DateField(label='Anfangsdatum', required=True,
                                 widget=admin.widgets.AdminDateWidget)
    end_date = forms.DateField(label='Enddatum', required=True,
                               widget=admin.widgets.AdminDateWidget)

    weekly = forms.ChoiceField(choices=[(7, 'jede Woche'), (14, 'Alle zwei Wochen')],
                               widget=forms.widgets.RadioSelect, initial=7)

    def __init__(self, *a, **k):
        super(JobCopyForm, self).__init__(*a, **k)
        inst = k.pop('instance')

        self.fields['start_date'].initial = inst.time.date() + datetime.timedelta(days=1)
        self.fields['time'].initial = inst.time
        self.fields['weekdays'].initial = [inst.time.isoweekday()]

    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        if 'start_date' in cleaned_data and 'end_date' in cleaned_data:
            if not self.get_dates(cleaned_data):
                raise ValidationError('Kein neuer Job fällt zwischen Anfangs- und Enddatum')
        return cleaned_data

    def save(self, commit=True):
        time = self.cleaned_data['time']

        inst = self.instance

        newjobs = []
        for date in self.get_dates(self.cleaned_data):
            dt = datetime.datetime.combine(date, time)
            job = RecuringJob.objects.create(type=inst.type, slots=inst.slots, time=dt)
            newjobs.append(job)
            job.save()

        # create new objects
        # HACK: admin expects a saveable object to be returned when commit=False
        # return newjobs[-1]
        return inst

    def save_m2m(self):
        # HACK: the admin expects this method to exist
        pass

    @staticmethod
    def get_dates(cleaned_data):
        start = cleaned_data['start_date']
        end = cleaned_data['end_date']
        weekdays = cleaned_data['weekdays']
        weekdays = set(int(i) for i in weekdays)
        res = []
        skip_even_weeks = cleaned_data['weekly'] == '14'
        for delta in range((end - start).days + 1):
            if skip_even_weeks and delta % 14 >= 7:
                continue
            date = start + datetime.timedelta(delta)
            if not date.isoweekday() in weekdays:
                continue
            res.append(date)
        return res


class AssignmentInline(admin.TabularInline):
    model = Assignment
    raw_id_fields = ['member']

    # can_delete = False

    # TODO: added these temporarily, need to be removed
    extra = 0
    max_num = 0

    def get_extra(self, request, obj=None, **kwargs):
        # TODO is this needed?
        # if 'copy_job' in request.path:
        #    return 0
        if obj is None:
            return 0
        return obj.freie_plaetze()

    def get_max_num(self, request, obj=None, **kwargs):
        if obj is None:
            return 0
        return obj.slots

class JobExtraInline(admin.TabularInline):
    model = JobExtra

    def get_extra(self, request, obj=None, **kwargs):
        return 0


class JobAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'type', 'time', 'slots', 'freie_plaetze']
    actions = ['copy_job', 'mass_copy_job']
    search_fields = ['type__name', 'type__activityarea__name']
    exclude = ['reminder_sent']
    inlines = [AssignmentInline]
    readonly_fields = ['freie_plaetze']

    def mass_copy_job(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, 'Genau 1 Job auswählen!', level=messages.ERROR)
            return HttpResponseRedirect('')

        inst, = queryset.all()
        return HttpResponseRedirect('copy_job/%s/' % inst.id)

    mass_copy_job.short_description = 'Job mehrfach kopieren...'

    def copy_job(self, request, queryset):
        for inst in queryset.all():
            newjob = RecuringJob(type=inst.type, slots=inst.slots, time=inst.time)
            newjob.save()

    copy_job.short_description = 'Jobs kopieren'

    def get_form(self, request, obj=None, **kwds):
        if 'copy_job' in request.path:
            return JobCopyForm
        return super(JobAdmin, self).get_form(request, obj, **kwds)

    def get_urls(self):
        urls = super(JobAdmin, self).get_urls()
        my_urls = [
            url(r'^copy_job/(?P<jobid>.*?)/$', self.admin_site.admin_view(self.copy_job_view))
        ]
        return my_urls + urls

    def copy_job_view(self, request, jobid):
        # HUGE HACK: modify admin properties just for this view
        tmp_readonly = self.readonly_fields
        tmp_inlines = self.inlines
        self.readonly_fields = []
        self.inlines = []
        res = self.change_view(request, jobid, extra_context={'title': 'Copy job'})
        self.readonly_fields = tmp_readonly
        self.inlines = tmp_inlines
        return res

    def get_queryset(self, request):
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            return qs.filter(type__activityarea__coordinator=request.user.member)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'type' and request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            kwargs['queryset'] = JobTypeDao.types_by_coordinator(request.user.member)
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class OneTimeJobAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'time', 'slots', 'freie_plaetze']
    actions = ['transform_job']
    search_fields = ['name', 'activityarea__name']
    exclude = ['reminder_sent']

    inlines = [AssignmentInline, JobExtraInline]
    readonly_fields = ['freie_plaetze']

    def transform_job(self, queryset):
        for inst in queryset.all():
            t = JobType()
            rj = RecuringJob()
            attribute_copy(inst, t)
            attribute_copy(inst, rj)
            name = t.name
            t.name = 'something temporal which possibly is never used'
            t.save()
            rj.type = t
            rj.save()
            for b in AssignmentDao.assignments_for_job(inst.id):
                b.job = rj
                b.save()
            inst.delete()
            t.name = name
            t.save()

    transform_job.short_description = 'EinzelJobs in Jobart konvertieren'

    def get_queryset(self, request):
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            return qs.filter(activityarea__coordinator=request.user.member)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'activityarea' and request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            kwargs['queryset'] = ActivityAreaDao.areas_by_coordinator(member)
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class JobTypeAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    actions = ['transform_job_type']
    inlines = [JobExtraInline]

    def transform_job_type(self, queryset):
        for inst in queryset.all():
            i = 0
            for rj in JobDao.recurings_by_type(inst.id):
                oj = OneTimeJob()
                attribute_copy(inst, oj)
                attribute_copy(rj, oj)
                oj.name += str(i)
                i += 1
                oj.save()
                for b in AssignmentDao.assignments_for_job(rj.id):
                    b.job = oj
                    b.save()
                rj.delete()
            inst.delete()

    transform_job_type.short_description = 'Jobart in EinzelJobs konvertieren'

    def get_queryset(self, request):
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            return qs.filter(activityarea__coordinator=request.user.member)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'activityarea' and request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            kwargs['queryset'] = ActivityAreaDao.areas_by_coordinator(request.user.member)
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ExtraSubscriptionInline(admin.TabularInline):
    model = ExtraSubscription
    fk_name = 'main_subscription'

    def get_extra(self, request, obj=None, **kwargs):
        return 0


class SubscriptionTypeInline(admin.TabularInline):
    model = Subscription.types.through
    verbose_name = 'Abo Typ'
    verbose_name_plural = 'Abo Typen'
    extra = 0

class FutureSubscriptionTypeInline(admin.TabularInline):
    model = Subscription.future_types.through
    verbose_name = 'Zukunft Abo Typ'
    verbose_name_plural = 'Zukunft Abo Typen'
    extra = 0

class SubscriptionAdmin(admin.ModelAdmin):
    form = SubscriptionAdminForm
    list_display = ['__str__', 'recipients_names', 'primary_member_nullsave', 'depot', 'active']
    # filter_horizontal = ['users']
    search_fields = ['members__user__username', 'members__first_name', 'members__last_name', 'depot__name']
    # raw_id_fields = ['primary_member']
    inlines = [SubscriptionTypeInline, FutureSubscriptionTypeInline, ExtraSubscriptionInline]


class AuditAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'source_type', 'target_type', 'field', 'action',
                    'source_object', 'target_object']
    # can_delete = False


class ShareAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'member', 'number', 'paid_date', 'issue_date', 'booking_date', 'cancelled_date',
                    'termination_date', 'payback_date']
    search_fields = ['id', 'member__email', 'member__first_name', 'member__last_name', 'number', 'paid_date',
                     'issue_date', 'booking_date', 'cancelled_date', 'termination_date', 'payback_date']
    raw_id_fields = ['member']


class DepotAdmin(admin.ModelAdmin):
    raw_id_fields = ['contact']
    list_display = ['name', 'code', 'weekday', 'contact']


class ExtraSubscriptionAdmin(admin.ModelAdmin):
    raw_id_fields = ['main_subscription']


class AreaAdmin(admin.ModelAdmin):
    filter_horizontal = ['members']
    raw_id_fields = ['coordinator']
    list_display = ['name', 'core', 'hidden', 'coordinator']

    def get_queryset(self, request):
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            return qs.filter(coordinator=request.user.member)
        return qs


class AssignmentAdmin(admin.ModelAdmin):
        
    raw_id_fields = ['member', 'job']
    

    def get_queryset(self, request):
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            return qs.filter(job__id__in=JobDao.ids_for_area_by_contact(request.user.member))
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'job' and request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            kwargs['queryset'] = JobDao.objects.filter(id__in=JobDao.ids_for_area_by_contact(request.user.member))
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class MemberAdminForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = '__all__'

    def __init__(self, *a, **k):
        forms.ModelForm.__init__(self, *a, **k)
        member = k.get('instance')
        if member is None:
            link = ''
        elif member.subscription:
            url = reverse('admin:juntagrico_subscription_change', args=(member.subscription.id,))
            link = '<a href=%s>%s</a>' % (url, member.subscription)
        else:
            link = 'Kein Abo'
        self.fields['subscription_link'].initial = link

    subscription_link = forms.URLField(widget=admin_util.MyHTMLWidget(), required=False,
                                       label='Abo')


class MemberAdmin(admin.ModelAdmin):
    form = MemberAdminForm
    list_display = ['email', 'first_name', 'last_name']
    search_fields = ['first_name', 'last_name', 'email']
    # raw_id_fields = ['subscription']
    exclude = ['subscription']
    readonly_fields = ['user']
    actions = ['impersonate_job']

    def impersonate_job(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, 'Genau 1 ' + Config.member_string() + ' auswählen!', level=messages.ERROR)
            return HttpResponseRedirect('')
        inst, = queryset.all()
        return HttpResponseRedirect('/impersonate/%s/' % inst.user.id)

    impersonate_job.short_description = Config.member_string() + ' imitieren (impersonate)...'


admin.site.register(Depot, DepotAdmin)
admin.site.register(ExtraSubscription, ExtraSubscriptionAdmin)
admin.site.register(ExtraSubscriptionType)
admin.site.register(ExtraSubscriptionCategory)
admin.site.register(SubscriptionSize)
admin.site.register(SubscriptionType)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(ActivityArea, AreaAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(MailTemplate)
admin.site.register(JobExtra)
admin.site.register(JobExtraType)
admin.site.register(JobType, JobTypeAdmin)
admin.site.register(RecuringJob, JobAdmin)
admin.site.register(OneTimeJob, OneTimeJobAdmin)
admin.site.register(ExtraSubBillingPeriod)
if Config.billing():
    admin.site.register(Bill)
    admin.site.register(Payment)
