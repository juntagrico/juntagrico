from django.contrib import admin
from django.db.models import Q, Max
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from polymorphic.admin import PolymorphicInlineSupportMixin

from juntagrico.admins import RichTextAdmin, OverrideFieldQuerySetMixin
from juntagrico.admins.inlines.contact_inline import ContactInline
from juntagrico.admins.inlines.job_extra_inline import JobExtraInline
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.dao.jobdao import JobDao
from juntagrico.dao.jobextradao import JobExtraDao
from juntagrico.dao.jobtypedao import JobTypeDao
from juntagrico.entity.jobs import OneTimeJob
from juntagrico.entity.location import Location
from juntagrico.util.admin import formfield_for_coordinator, queryset_for_coordinator
from juntagrico.util.models import attribute_copy


class JobTypeAdmin(PolymorphicInlineSupportMixin, OverrideFieldQuerySetMixin, RichTextAdmin):
    fields = ('name', 'displayed_name', 'activityarea', 'location', 'default_duration', 'description', 'visible')
    list_display = ['__str__', 'default_duration', 'location', 'contacts_text', 'visible', 'last_used']
    list_filter = (('activityarea', admin.RelatedOnlyFieldListFilter), 'visible')
    autocomplete_fields = ['activityarea', 'location']
    search_fields = ['name', 'activityarea__name', 'last_used']
    actions = ['transform_job_type', 'action_hide', 'action_make_visible']
    inlines = [ContactInline, JobExtraInline]

    @admin.display(
        ordering='last_used',
        description=_('Zuletzt verwendet')
    )
    def last_used(self, instance):
        return instance.last_used

    @admin.display(description=_('Kontakt'))
    def contacts_text(self, instance):
        return mark_safe("<br>".join([str(c) for c in instance.contacts]))

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

    @admin.action(description=_('Verstecken'))
    def action_hide(self, request, queryset):
        # clear order, because update can not be applied when ordered by aggregate
        queryset.order_by().update(visible=False)

    @admin.action(description=_('Sichtbar machen'))
    def action_make_visible(self, request, queryset):
        # clear order, because update can not be applied when ordered by aggregate
        queryset.order_by().update(visible=True)

    def get_location_queryset(self, request, obj):
        return Location.objects.exclude(Q(visible=False), ~Q(jobtype=obj))

    def get_queryset(self, request):
        qs = queryset_for_coordinator(self, request, 'activityarea__coordinator')
        qs = qs.annotate(last_used=Max('recuringjob__time'))
        return qs

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if 'autocomplete' in request.path and request.GET.get('model_name') == 'recuringjob' and request.GET.get(
                'field_name') == 'type':
            queryset = queryset.filter(visible=True)
            if request.user.has_perm('juntagrico.is_area_admin') and (
                    not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
                queryset = queryset.intersection(JobTypeDao.visible_types_by_coordinator(request.user.member))
        return queryset, use_distinct

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = formfield_for_coordinator(request,
                                           db_field.name,
                                           'activityarea',
                                           'juntagrico.is_area_admin',
                                           ActivityAreaDao.areas_by_coordinator)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
