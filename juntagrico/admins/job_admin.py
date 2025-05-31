from datetime import timedelta, datetime, date

from django.urls import path, reverse
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from polymorphic.admin import PolymorphicInlineSupportMixin

from juntagrico.admins import RichTextAdmin, AreaCoordinatorMixin, can_see_all
from juntagrico.admins.admin_decorators import single_element_action
from juntagrico.admins.filters import FutureDateTimeFilter
from juntagrico.admins.forms.job_copy_form import JobMassCopyForm, JobMassCopyToFutureForm, \
    OnlyFutureJobForm, JobCopyForm, JobCopyToFutureForm
from juntagrico.admins.inlines.assignment_inline import AssignmentInline
from juntagrico.admins.inlines.contact_inline import ContactInline
from juntagrico.entity.jobs import RecuringJob, JobType
from juntagrico.templatetags.juntagrico.common import richtext


def type_div(field, value=None):
    value = value or _('(Wähle eine Jobart aus)')
    return mark_safe(
        '<div id="id_type_' + field + '" '
            'data-url="' + reverse('api-jobtype-' + field, args=[99]) + '">' +
            str(value) +
        '</div>'
    )


class OnlyFutureJobMixin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return (obj is None or obj.check_if(request.user).can_modify()) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return (obj is None or obj.check_if(request.user).can_modify()) and super().has_delete_permission(request, obj)

    def get_form(self, request, obj=None, **kwds):
        if not request.user.has_perm('juntagrico.can_edit_past_jobs'):
            kwds['form'] = OnlyFutureJobForm
        return super().get_form(request, obj, **kwds)


class JobCopy(admin.ModelAdmin):
    """ All overrides for the mass copy view
    """
    copy_fields = ('type', 'time', ('duration_override', 'type_duration'), 'multiplier', ('slots', 'infinite_slots'),
              'type_description', 'additional_description', 'pinned')
    copy_fieldsets = [
        (None, {'fields': [
            'type', ('duration_override', 'type_duration'), 'multiplier', ('slots', 'infinite_slots'),
            'type_description', 'additional_description'
        ]}),
        (gettext_lazy('Kopieren nach'), {'fields': [
            'new_time', 'start_date', 'end_date', 'weekdays', 'weekly'
        ]}),
    ]
    copy_readonly_fields = ['type_description', 'type_duration']

    def get_urls(self):
        hide_buttons = {
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': False,
        }
        copy_urls = [
            path('<str:object_id>/copy/multiple', self.admin_site.admin_view(self.change_view), {
                'extra_context': {'title': _('Job mehrfach kopieren'), **hide_buttons}
            }, name='action-mass-copy-job'),
            path('<str:object_id>/copy/', self.admin_site.admin_view(self.change_view), {
                'extra_context': {'title': _('Job kopieren'), **hide_buttons}
            }, name='action-copy-job'),
        ]
        return copy_urls + super().get_urls()

    @staticmethod
    def is_mass_copy_view(request):
        return request.resolver_match.url_name == 'action-mass-copy-job'

    @staticmethod
    def is_copy_view(request):
        return request.resolver_match.url_name == 'action-copy-job'

    def get_form(self, request, obj=None, **kwds):
        # return forms for mass copy
        if self.is_mass_copy_view(request):
            if request.user.has_perm('juntagrico.can_edit_past_jobs'):
                kwds['form'] = JobMassCopyForm
            else:
                kwds['form'] = JobMassCopyToFutureForm
        elif self.is_copy_view(request):
            if request.user.has_perm('juntagrico.can_edit_past_jobs'):
                kwds['form'] = JobCopyForm
            else:
                kwds['form'] = JobCopyToFutureForm
        return super().get_form(request, obj, **kwds)

    def has_change_permission(self, request, obj=None):
        can_copy = self.is_mass_copy_view(request) and super().has_add_permission(request)
        return can_copy or super().has_change_permission(request, obj)

    def get_fields(self, request, obj=None):
        if self.is_mass_copy_view(request):
            return None
        elif self.is_copy_view(request):
            return self.copy_fields
        return super().get_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        if self.is_mass_copy_view(request):
            return self.copy_fieldsets
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if self.is_mass_copy_view(request):
            return self.copy_readonly_fields  # special case for mass job copy action
        return super().get_readonly_fields(request, obj)

    def get_inlines(self, request, obj):
        if self.is_mass_copy_view(request) or self.is_copy_view(request):
            return [ContactInline]  # special case for mass job copy action
        return super().get_inlines(request, obj)

    def save_related(self, request, form, formsets, change):
        if self.is_mass_copy_view(request) or self.is_copy_view(request):
            form.save_related(formsets)
        else:
            super().save_related(request, form, formsets, change)

    def response_change(self, request, obj):
        if self.is_copy_view(request):
            # show new job on page
            return HttpResponseRedirect(reverse('job', args=[obj.id]))
        return super().response_change(request, obj)


class JobAdmin(PolymorphicInlineSupportMixin, AreaCoordinatorMixin, RichTextAdmin, OnlyFutureJobMixin, JobCopy):
    fields = ('type', 'time', ('duration_override', 'type_duration'), 'multiplier', ('slots', 'infinite_slots', 'free_slots'),
              'type_description', 'additional_description', 'pinned', 'canceled')
    list_display = ['__str__', 'type', 'time', 'slots', 'duration', 'multiplier', 'slots_display', 'free_slots_display', 'pinned', 'canceled']
    list_filter = (('type__activityarea', admin.RelatedOnlyFieldListFilter), ('time', FutureDateTimeFilter))
    actions = ['copy_job', 'mass_copy_job']
    search_fields = ['type__name', 'type__activityarea__name', 'time']
    date_hierarchy = 'time'
    exclude = ['reminder_sent']
    autocomplete_fields = ['type']
    inlines = [ContactInline, AssignmentInline]
    readonly_fields = ['free_slots', 'type_description', 'type_duration']
    path_to_area = 'type__activityarea'

    @admin.display(description=_('Beschreibung der Jobart'))
    def type_description(self, instance):
        # when adding a new job, instance is an empty job queryset
        return type_div('description', richtext(instance.type.description) if instance.type_id else None)

    @admin.display(description=_('Standardwert'))
    def type_duration(self, instance):
        return type_div('duration', instance.type.default_duration if instance.type_id else None)

    @admin.action(description=_('Job mehrfach kopieren...'))
    @single_element_action('Genau 1 Job auswählen!')
    def mass_copy_job(self, request, queryset):
        inst = queryset.first()
        return HttpResponseRedirect(reverse('admin:action-mass-copy-job', args=[inst.id]))

    @admin.action(description=_('Jobs kopieren'))
    def copy_job(self, request, queryset):
        for instance in queryset.all():
            time = instance.time
            if not request.user.has_perm('juntagrico.can_edit_past_jobs') and time <= timezone.now():
                # create copy in future if job is in past and member can't edit past jobs
                time = datetime.combine(date.today() + timedelta(7), time.time())
            new_job = RecuringJob(type=instance.type, slots=instance.slots, time=time)
            new_job.save()

    def get_area(self, obj):
        return obj.type.activityarea

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # used for form validation
        if db_field.name == 'type':
            user = request.user
            if not can_see_all(user, 'jobtype'):
                kwargs["queryset"] = JobType.objects.filter(
                    activityarea__coordinator_access__member__user=user,
                    activityarea__coordinator_access__can_modify_jobs=True
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ["juntagrico/js/job_admin.js"]
