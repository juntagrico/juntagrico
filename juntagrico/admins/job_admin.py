from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _

from juntagrico.admins import RichTextAdmin
from juntagrico.admins.admin_decorators import single_element_action
from juntagrico.admins.filters import FutureDateTimeFilter
from juntagrico.admins.forms.job_copy_form import JobCopyForm
from juntagrico.admins.inlines.assignment_inline import AssignmentInline
from juntagrico.dao.jobtypedao import JobTypeDao
from juntagrico.entity.jobs import RecuringJob, JobType
from juntagrico.util.admin import formfield_for_coordinator, queryset_for_coordinator


class JobAdmin(RichTextAdmin):
    list_display = ['__str__', 'type', 'time', 'slots', 'free_slots']
    list_filter = ('type__activityarea', ('time', FutureDateTimeFilter))
    actions = ['copy_job', 'mass_copy_job']
    search_fields = ['type__name', 'type__activityarea__name', 'time']
    exclude = ['reminder_sent']
    inlines = [AssignmentInline]
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
            url(r'^copy_job/(?P<jobid>.*?)/$',
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
