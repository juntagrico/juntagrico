from datetime import timedelta, datetime, date

from django import forms
from django.core.exceptions import ValidationError
from django.urls import path, reverse
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from polymorphic.admin import PolymorphicInlineSupportMixin

from juntagrico.admins import RichTextAdmin, OverrideFieldQuerySetMixin
from juntagrico.admins.admin_decorators import single_element_action
from juntagrico.admins.filters import FutureDateTimeFilter
from juntagrico.admins.forms.job_copy_form import JobCopyForm, JobCopyToFutureForm
from juntagrico.admins.inlines.assignment_inline import AssignmentInline
from juntagrico.admins.inlines.contact_inline import ContactInline
from juntagrico.dao.jobtypedao import JobTypeDao
from juntagrico.entity.jobs import RecuringJob, JobType
from juntagrico.util.admin import formfield_for_coordinator, queryset_for_coordinator


def can_edit_past_jobs(request):
    return request.user.is_superuser or request.user.has_perm('juntagrico.can_edit_past_jobs')


class OnlyFutureJobAdminForm(forms.ModelForm):
    def clean_time(self):
        time = self.cleaned_data['time']
        if time <= timezone.now():
            raise ValidationError(_('Neue Jobs können nicht in der Vergangenheit liegen.'))
        return time


def type_div(field, value=None):
    value = value or _('(Wähle eine Jobart aus)')
    return mark_safe(
        '<div id="id_type_' + field + '" '
            'data-url="' + reverse('api-jobtype-' + field, args=[99]) + '">' +
            str(value) +
        '</div>'
    )


class JobAdmin(PolymorphicInlineSupportMixin, OverrideFieldQuerySetMixin, RichTextAdmin):
    fields = ('type', 'time', ('duration_override', 'type_duration'), 'multiplier', ('slots', 'infinite_slots', 'free_slots'),
              'type_description', 'additional_description', 'pinned', 'canceled')
    list_display = ['__str__', 'type', 'time', 'slots', 'free_slots']
    list_filter = (('type__activityarea', admin.RelatedOnlyFieldListFilter), ('time', FutureDateTimeFilter))
    actions = ['copy_job', 'mass_copy_job']
    search_fields = ['type__name', 'type__activityarea__name', 'time']
    exclude = ['reminder_sent']
    autocomplete_fields = ['type']
    inlines = [ContactInline, AssignmentInline]
    readonly_fields = ['free_slots', 'type_description', 'type_duration']

    @admin.display(description=_('Beschreibung der Jobart'))
    def type_description(self, instance):
        # when adding a new job, instance is an empty job queryset
        return type_div('description', instance.type.description if instance.type_id else None)

    @admin.display(description=_('Standardwert'))
    def type_duration(self, instance):
        return type_div('duration', instance.type.default_duration if instance.type_id else None)

    def has_change_permission(self, request, obj=None):
        return (self.is_copy_view(request) or obj is None or obj.can_modify(request)
                ) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return (self.is_copy_view(request) or obj is None or obj.can_modify(request)
                ) and super().has_delete_permission(request, obj)

    def get_fields(self, request, obj=None):
        if self.is_copy_view(request):
            original_fields = self.fields
            self.fields = None
            fields = super().get_fields(request, obj)
            self.fields = original_fields
            return fields
        return super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if self.is_copy_view(request):
            return []  # special case for mass job copy action
        return super().get_readonly_fields(request, obj)

    def get_inlines(self, request, obj):
        if self.is_copy_view(request):
            return [ContactInline]  # special case for mass job copy action
        return super().get_inlines(request, obj)

    def save_related(self, request, form, formsets, change):
        if self.is_copy_view(request):
            form.save_related(formsets)
        else:
            super().save_related(request, form, formsets, change)

    @admin.action(description=_('Job mehrfach kopieren...'))
    @single_element_action('Genau 1 Job auswählen!')
    def mass_copy_job(self, request, queryset):
        inst = queryset.first()
        return HttpResponseRedirect(reverse('admin:action-mass-copy-job', args=[inst.id]))

    @admin.action(description=_('Jobs kopieren'))
    def copy_job(self, request, queryset):
        for inst in queryset.all():
            time = inst.time
            if not can_edit_past_jobs(request) and time <= timezone.now():
                # create copy in future if job is in past and member can't edit past jobs
                time = datetime.combine(date.today() + timedelta(7), time.time())
            newjob = RecuringJob(type=inst.type, slots=inst.slots, time=time)
            newjob.save()

    def get_form(self, request, obj=None, **kwds):
        # return forms for mass copy
        if self.is_copy_view(request):
            if can_edit_past_jobs(request):
                return JobCopyForm
            return JobCopyToFutureForm
        # or return normal edit forms
        elif not can_edit_past_jobs(request):
            kwds['form'] = OnlyFutureJobAdminForm
        return super().get_form(request, obj, **kwds)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('mass_copy_job/<str:jobid>/',
                 self.admin_site.admin_view(self.copy_job_view), name='action-mass-copy-job')
        ]
        return my_urls + urls

    @staticmethod
    def is_copy_view(request):
        return request.resolver_match.url_name == 'action-mass-copy-job'

    def copy_job_view(self, request, jobid):
        res = self.change_view(request, jobid, extra_context={'title': 'Copy job'})
        return res

    def get_queryset(self, request):
        return queryset_for_coordinator(self, request, 'type__activityarea__coordinator')

    def get_type_queryset(self, request, obj):
        visible_by_coordinator = formfield_for_coordinator(
            request, None, None, 'juntagrico.is_area_admin',
            JobTypeDao.visible_types_by_coordinator,
            queryset=JobTypeDao.visible_types()
        )['queryset']
        return (JobType.objects.filter(recuringjob=obj) | visible_by_coordinator).distinct()

    class Media:
        js = ["juntagrico/js/job_admin.js"]
