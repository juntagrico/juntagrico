from django.utils.translation import gettext as _

from juntagrico.admins import BaseAdmin
from juntagrico.admins.filters import FutureDateTimeFilter
from juntagrico.admins.inlines.assignment_inline import AssignmentInline
from juntagrico.admins.inlines.job_extra_inline import JobExtraInline
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.entity.jobs import JobType, RecuringJob, OneTimeJob
from juntagrico.util.admin import formfield_for_coordinator, queryset_for_coordinator, extra_context_for_past_jobs
from juntagrico.util.models import attribute_copy


class OneTimeJobAdmin(BaseAdmin):
    list_display = ['__str__', 'time', 'slots', 'free_slots']
    list_filter = ('activityarea', ('time', FutureDateTimeFilter))
    actions = ['transform_job']
    search_fields = ['name', 'activityarea__name', 'time']
    exclude = ['reminder_sent']

    inlines = [AssignmentInline, JobExtraInline]
    readonly_fields = ['free_slots']

    def transform_job(self, request, queryset):
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

    transform_job.short_description = _('EinzelJobs in Jobart konvertieren')

    def get_queryset(self, request):
        return queryset_for_coordinator(self, request, 'activityarea__coordinator')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = formfield_for_coordinator(request,
                                           db_field.name,
                                           'activityarea',
                                           'juntagrico.is_area_admin',
                                           ActivityAreaDao.areas_by_coordinator)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context_for_past_jobs(request, OneTimeJob, object_id, extra_context)
        return super().change_view(request, object_id, extra_context=extra_context)
