from django.conf.urls import url
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.admins import RichTextAdmin
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

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        job_is_in_past = obj.end_time() < timezone.now()
        job_is_running = obj.start_time() < timezone.now()
        job_canceled = obj.canceled
        job_read_only = job_canceled or job_is_running or job_is_in_past
        if job_read_only and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.can_edit_past_jobs'))):
            for inline in self.inlines:
                inline.readonly_fields = [field.name for field in inline.model._meta.fields]
            return [field.name for field in obj._meta.fields]
        return self.readonly_fields

    def mass_copy_job(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request, _('Genau 1 Job auswählen!'), level=messages.ERROR)
            return HttpResponseRedirect('')

        inst, = queryset.all()
        return HttpResponseRedirect('copy_job/%s/' % inst.id)

    mass_copy_job.short_description = _('Job mehrfach kopieren...')

    def copy_job(self, request, queryset):
        for inst in queryset.all():
            newjob = RecuringJob(
                type=inst.type, slots=inst.slots, time=inst.time)
            newjob.save()

    copy_job.short_description = _('Jobs kopieren')

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
