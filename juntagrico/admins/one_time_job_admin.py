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
from juntagrico.entity.location import Location


class OneTimeJobAdmin(PolymorphicInlineSupportMixin, OverrideFieldQuerySetMixin, RichTextAdmin, OnlyFutureJobMixin,
                      JobTypeBaseAdmin):
    fields = ('name', 'displayed_name', 'activityarea', 'location', 'time', 'default_duration', 'multiplier',
              ('slots', 'infinite_slots', 'free_slots'), 'description', 'pinned', 'canceled')
    list_display = ['__str__', 'time', 'default_duration', 'multiplier', 'slots_display', 'free_slots_display', 'pinned', 'canceled']
    list_filter = (('activityarea', admin.RelatedOnlyFieldListFilter), ('time', FutureDateTimeFilter))
    actions = ['transform_job']
    search_fields = ['name', 'displayed_name', 'activityarea__name', 'time']
    date_hierarchy = 'time'
    exclude = ['reminder_sent']
    autocomplete_fields = ['activityarea', 'location']

    inlines = [ContactInlineForJob, AssignmentInline, JobExtraInlineForOnetimeJob]
    readonly_fields = ['free_slots']

    @admin.action(description=_('EinzelJobs in Jobart konvertieren'))
    def transform_job(self, request, queryset):
        for inst in queryset.all():
            inst.convert()

    def get_location_queryset(self, request, obj):
        return Location.objects.exclude(Q(visible=False), ~Q(onetimejob=obj))
