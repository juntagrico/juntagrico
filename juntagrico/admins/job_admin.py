from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import re_path
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from polymorphic.admin import PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, \
    PolymorphicChildModelFilter

from juntagrico.admins import RichTextAdmin
from juntagrico.admins.admin_decorators import single_element_action
from juntagrico.admins.filters import FutureDateTimeFilter
from juntagrico.admins.forms.job_copy_form import JobCopyForm
from juntagrico.admins.inlines.assignment_inline import AssignmentInline
from juntagrico.admins.inlines.contact_inline import ContactInline
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.jobtypedao import JobTypeDao
from juntagrico.entity.jobs import RecuringJob, JobType, OneTimeJob
from juntagrico.util.admin import formfield_for_coordinator, queryset_for_coordinator


class ActivityAreaFilter(admin.SimpleListFilter):
    title = _('Tätigkeitsbereich')
    parameter_name = "area"

    def lookups(self, request, model_admin):
        qs = ActivityAreaDao.all_visible_areas_ordered()
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            qs = qs.filter(coordinator=request.user.member)
        return qs.values_list('id', 'name')

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except TypeError:
            value = None
        if value:
            # check permission
            for choice_value in self.lookup_choices:
                if choice_value[0] == value:
                    return queryset.filter(
                        Q(RecuringJob___type__activityarea=value) | Q(OneTimeJob___activityarea=value))
            raise PermissionDenied(_('Kein Zugriff auf Tätigkeitsbereich "{}".'.format(value)))
        return queryset


# Known issues: Children are visible in sidebar https://github.com/django-polymorphic/django-polymorphic/issues/497
class AbstractJobAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    child_models = (RecuringJob, OneTimeJob)
    polymorphic_list = True
    list_display = ['__str__', 'type', 'time', 'slots', 'free_slots']
    list_filter = (PolymorphicChildModelFilter, ActivityAreaFilter, ('time', FutureDateTimeFilter))
    search_fields = ['RecuringJob___type__name', 'RecuringJob___type__activityarea__name',
                     'OneTimeJob___activityarea__name', 'OneTimeJob___name', 'time']
    # TODO: combine actions of child classes

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            member = request.user.member
            return qs.filter(
                Q(RecuringJob___type__activityarea__coordinator=member) | Q(
                    OneTimeJob___activityarea__coordinator=member))
        return qs


class JobAdmin(PolymorphicInlineSupportMixin, RichTextAdmin, PolymorphicChildModelAdmin):
    base_model = RecuringJob
    list_display = ['__str__', 'type', 'time', 'slots', 'free_slots']
    list_filter = ('type__activityarea', ('time', FutureDateTimeFilter))
    actions = ['copy_job', 'mass_copy_job']
    search_fields = ['type__name', 'type__activityarea__name', 'time']

    exclude = ['reminder_sent']
    inlines = [ContactInline, AssignmentInline]
    readonly_fields = ['free_slots']

    def has_change_permission(self, request, obj=None):
        return (obj is None or obj.can_modify(request)) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return (obj is None or obj.can_modify(request)) and super().has_delete_permission(request, obj)

    @admin.action(description=_('Job mehrfach kopieren...'))
    @single_element_action('Genau 1 Job auswählen!')
    def mass_copy_job(self, request, queryset):
        inst, = queryset.all()
        return HttpResponseRedirect('copy_job/%s/' % inst.id)

    @admin.action(description=_('Jobs kopieren'))
    def copy_job(self, request, queryset):
        for inst in queryset.all():
            newjob = RecuringJob(
                type=inst.type, slots=inst.slots, time=inst.time)
            newjob.save()

    def get_form(self, request, obj=None, **kwds):
        if 'copy_job' in request.path:
            return JobCopyForm
        return super().get_form(request, obj, **kwds)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'^copy_job/(?P<jobid>.*?)/$',
                    self.admin_site.admin_view(self.copy_job_view))
        ]
        return my_urls + urls

    def copy_job_view(self, request, jobid):
        # HUGE HACK: modify admin properties just for this view
        tmp_readonly = self.readonly_fields
        tmp_inlines = self.inlines
        self.readonly_fields = []
        self.inlines = []
        res = self.change_view(request, jobid, extra_context={
            'title': 'Copy job'})
        self.readonly_fields = tmp_readonly
        self.inlines = tmp_inlines
        return res

    def get_queryset(self, request):
        return queryset_for_coordinator(self, request, 'type__activityarea__coordinator')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'type':
            kwargs['queryset'] = JobTypeDao.visible_types()
            kwargs = formfield_for_coordinator(request,
                                               db_field.name,
                                               'type',
                                               'juntagrico.is_area_admin',
                                               JobTypeDao.visible_types_by_coordinator,
                                               **kwargs)
            # show jobtype even if invisible to be able to edit and save this job with the same type
            # HACK: get instance via url argument
            instance_pk = request.resolver_match.kwargs.get('object_id')
            if instance_pk is not None:
                kwargs['queryset'] |= JobType.objects.filter(recuringjob__pk=instance_pk)
                kwargs['queryset'] = kwargs['queryset'].distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
