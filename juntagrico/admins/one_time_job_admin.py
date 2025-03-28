from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext as _
from polymorphic.admin import PolymorphicInlineSupportMixin

from juntagrico.admins import RichTextAdmin, OverrideFieldQuerySetMixin
from juntagrico.admins.filters import FutureDateTimeFilter
from juntagrico.admins.inlines.assignment_inline import AssignmentInline
from juntagrico.admins.inlines.contact_inline import ContactInline
from juntagrico.admins.inlines.job_extra_inline import JobExtraInline
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.entity.jobs import JobType, RecuringJob
from juntagrico.entity.location import Location
from juntagrico.util.admin import formfield_for_coordinator, queryset_for_coordinator
from juntagrico.util.models import attribute_copy


class OneTimeJobAdmin(PolymorphicInlineSupportMixin, OverrideFieldQuerySetMixin, RichTextAdmin):
    fields = ('name', 'displayed_name', 'activityarea', 'location', 'time', 'default_duration', 'multiplier',
              ('slots', 'infinite_slots', 'free_slots'), 'description', 'pinned', 'canceled')
    list_display = ['__str__', 'time', 'slots', 'free_slots']
    list_filter = ('activityarea', ('time', FutureDateTimeFilter))
    actions = ['transform_job']
    search_fields = ['name', 'activityarea__name', 'time']
    exclude = ['reminder_sent']
    autocomplete_fields = ['activityarea', 'location']

    inlines = [ContactInline, AssignmentInline, JobExtraInline]
    readonly_fields = ['free_slots']

    def has_change_permission(self, request, obj=None):
        return (obj is None or obj.can_modify(request)) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return (obj is None or obj.can_modify(request)) and super().has_delete_permission(request, obj)

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

    def get_queryset(self, request):
        return queryset_for_coordinator(self, request, 'activityarea__coordinator')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = formfield_for_coordinator(request,
                                           db_field.name,
                                           'activityarea',
                                           'juntagrico.is_area_admin',
                                           ActivityAreaDao.areas_by_coordinator)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
