from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext as _
from polymorphic.admin import PolymorphicInlineSupportMixin

from juntagrico.admins import RichTextAdmin
from juntagrico.admins.inlines.contact_inline import ContactInline
from juntagrico.admins.inlines.job_extra_inline import JobExtraInline
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.dao.jobdao import JobDao
from juntagrico.dao.jobextradao import JobExtraDao
from juntagrico.entity.jobs import OneTimeJob
from juntagrico.entity.location import Location
from juntagrico.util.admin import formfield_for_coordinator, queryset_for_coordinator
from juntagrico.util.models import attribute_copy


class JobTypeAdmin(PolymorphicInlineSupportMixin, RichTextAdmin):
    list_display = ['__str__', 'activityarea',
                    'default_duration', 'location', 'visible']
    list_filter = ('activityarea', 'visible')
    actions = ['transform_job_type']
    inlines = [ContactInline, JobExtraInline]

    @admin.action(description=_('Jobart in EinzelJobs konvertieren'))
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
                for je in JobExtraDao.by_type(inst.id):
                    je.recuring_type = None
                    je.onetime_type = oj
                    je.pk = None
                    je.save()
                for b in AssignmentDao.assignments_for_job(rj.id):
                    b.job = oj
                    b.save()
                rj.delete()
            for je in JobExtraDao.by_type(inst.id):
                je.delete()
            inst.delete()

    def get_form(self, request, obj=None, **kwds):
        form = super().get_form(request, obj, **kwds)
        # only include visible and current locations in choices
        # filter queryset here, because here the obj is available
        form.base_fields['location'].queryset = Location.objects.exclude(Q(visible=False), ~Q(jobtype=obj))
        return form

    def get_queryset(self, request):
        qs = queryset_for_coordinator(self, request, 'activityarea__coordinator')
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = formfield_for_coordinator(request,
                                           db_field.name,
                                           'activityarea',
                                           'juntagrico.is_area_admin',
                                           ActivityAreaDao.areas_by_coordinator)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
