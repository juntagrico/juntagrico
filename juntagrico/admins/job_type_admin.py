from django.contrib import admin
from django.utils.translation import gettext as _

from juntagrico.admins.inlines.job_extra_inline import JobExtraInline
from juntagrico.entity.jobs import OneTimeJob
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.dao.jobdao import JobDao
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.util.addons import get_jobtype_inlines
from juntagrico.util.models import attribute_copy


class JobTypeAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    actions = ['transform_job_type']
    inlines = [JobExtraInline]

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_jobtype_inlines())
        super(JobTypeAdmin, self).__init__(*args, **kwargs)

    def transform_job_type(self, request, queryset):
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

    transform_job_type.short_description = _('Jobart in EinzelJobs konvertieren')

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
