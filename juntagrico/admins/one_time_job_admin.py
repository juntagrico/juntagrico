from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext as _
from polymorphic.admin import PolymorphicInlineSupportMixin

from juntagrico.admins import RichTextAdmin, OverrideFieldQuerySetMixin
from juntagrico.admins.filters import FutureDateTimeFilter
from juntagrico.admins.inlines.assignment_inline import AssignmentInline
from juntagrico.admins.inlines.contact_inline import ContactInlineForJob
from juntagrico.admins.inlines.job_extra_inline import JobExtraInlineForOnetimeJob
from juntagrico.admins.job_admin import OnlyFutureJobMixin
from juntagrico.admins.job_type_admin import JobTypeBaseAdmin
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.entity.jobs import JobType, RecuringJob
from juntagrico.entity.location import Location
from juntagrico.util.models import attribute_copy


class OneTimeJobAdmin(PolymorphicInlineSupportMixin, OverrideFieldQuerySetMixin, RichTextAdmin, OnlyFutureJobMixin,
                      JobTypeBaseAdmin):
    fields = ('name', 'displayed_name', 'activityarea', 'location', 'time', 'default_duration', 'multiplier',
              ('slots', 'infinite_slots', 'free_slots'), 'description', 'pinned', 'canceled')
    list_display = ['__str__', 'time', 'default_duration', 'multiplier', 'slots_display', 'free_slots_display', 'pinned', 'canceled']
    list_filter = (('activityarea', admin.RelatedOnlyFieldListFilter), ('time', FutureDateTimeFilter))
    actions = ['transform_job']
    search_fields = ['name', 'activityarea__name', 'time']
    date_hierarchy = 'time'
    exclude = ['reminder_sent']
    autocomplete_fields = ['activityarea', 'location']

    inlines = [ContactInlineForJob, AssignmentInline, JobExtraInlineForOnetimeJob]
    readonly_fields = ['free_slots']

    @admin.action(description=_('EinzelJobs in Jobart konvertieren'))
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

    def get_location_queryset(self, request, obj):
        return Location.objects.exclude(Q(visible=False), ~Q(onetimejob=obj))
