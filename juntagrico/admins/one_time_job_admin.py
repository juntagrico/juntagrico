from django.contrib import admin
from django.utils.translation import gettext as _

from juntagrico.admins.inlines.assignment_inline import AssignmentInline
from juntagrico.admins.inlines.job_extra_inline import JobExtraInline
from juntagrico.entity.jobs import JobType, RecuringJob
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.util.addons import get_otjob_inlines
from juntagrico.util.models import attribute_copy


class OneTimeJobAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'time', 'slots', 'free_slots']
    actions = ['transform_job']
    search_fields = ['name', 'activityarea__name']
    exclude = ['reminder_sent']

    inlines = [AssignmentInline, JobExtraInline]
    readonly_fields = ['free_slots']

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_otjob_inlines())
        super(OneTimeJobAdmin, self).__init__(*args, **kwargs)

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
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            return qs.filter(activityarea__coordinator=request.user.member)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'activityarea' and request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            kwargs['queryset'] = ActivityAreaDao.areas_by_coordinator(
                request.user.member)
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
