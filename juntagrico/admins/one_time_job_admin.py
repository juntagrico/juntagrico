from django.contrib import admin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.translation import gettext as _
from polymorphic.admin import PolymorphicInlineSupportMixin

from juntagrico.admins import RichTextAdmin, OverrideFieldQuerySetMixin
from juntagrico.admins.filters import FutureDateTimeFilter
from juntagrico.admins.forms.job_copy_form import OnetimeJobCopyForm, OneTimeJobCopyToFutureForm
from juntagrico.admins.inlines.assignment_inline import AssignmentInline
from juntagrico.admins.inlines.contact_inline import ContactInlineForJob
from juntagrico.admins.inlines.job_extra_inline import JobExtraInlineForOnetimeJob
from juntagrico.admins.job_admin import OnlyFutureJobMixin
from juntagrico.admins.job_type_admin import JobTypeBaseAdmin
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.entity.jobs import JobType, RecuringJob
from juntagrico.entity.location import Location
from juntagrico.util.models import attribute_copy


class OneTimeJobCopy(admin.ModelAdmin):
    """ All overrides for the copy view
    """
    copy_fields = (
        'name', 'displayed_name', 'activityarea', 'location', 'time',
        'default_duration', 'multiplier', ('slots', 'infinite_slots'),
        'description', 'pinned'
    )

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        # self.save_as = self.is_copy_view(request)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        copy_urls = [
            path('<str:object_id>/copy/', self.admin_site.admin_view(self.change_view), {
                'extra_context': {'title': _('EinzelJob kopieren'), 'is_copy_view': True}
            }, name='action-copy-onetime-job'),
        ]
        return copy_urls + super().get_urls()

    @staticmethod
    def is_copy_view(request):
        return request.resolver_match.url_name == 'action-copy-onetime-job'

    def get_form(self, request, obj=None, **kwds):
        if self.is_copy_view(request):
            if request.user.has_perm('juntagrico.can_edit_past_jobs'):
                kwds['form'] = OnetimeJobCopyForm
            else:
                kwds['form'] = OneTimeJobCopyToFutureForm
        return super().get_form(request, obj, **kwds)

    def has_change_permission(self, request, obj=None):
        # to copy, add permission is sufficient
        can_copy = self.is_copy_view(request) and super().has_add_permission(request)
        return can_copy or super().has_change_permission(request, obj)

    def get_fields(self, request, obj=None):
        if self.is_copy_view(request):
            return self.copy_fields
        return super().get_fields(request, obj)

    def get_inlines(self, request, obj):
        if self.is_copy_view(request):
            return [ContactInlineForJob, JobExtraInlineForOnetimeJob]
        return super().get_inlines(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if self.is_copy_view(request):
            # show new job on page
            return HttpResponseRedirect(reverse('job', args=[obj.id]))
        return super().response_add(request, obj, post_url_continue)


class OneTimeJobAdmin(PolymorphicInlineSupportMixin, OverrideFieldQuerySetMixin, RichTextAdmin, OneTimeJobCopy, OnlyFutureJobMixin,
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
