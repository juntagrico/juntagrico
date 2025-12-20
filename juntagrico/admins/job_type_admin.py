from django.contrib import admin
from django.db.models import Q, Max
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from polymorphic.admin import PolymorphicInlineSupportMixin

from juntagrico.admins import RichTextAdmin, OverrideFieldQuerySetMixin, AreaCoordinatorMixin, can_see_all
from juntagrico.admins.inlines.contact_inline import ContactInlineForJob
from juntagrico.admins.inlines.job_extra_inline import JobExtraInlineForJobType
from juntagrico.entity.jobs import ActivityArea
from juntagrico.entity.location import Location


class JobTypeBaseAdmin(AreaCoordinatorMixin):
    path_to_area = 'activityarea'

    def get_area(self, obj):
        return obj.activityarea

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # used for form validation
        if db_field.name == 'activityarea':
            user = request.user
            if not can_see_all(user, 'activityarea'):
                kwargs["queryset"] = ActivityArea.objects.filter(
                    coordinator_access__member__user=user,
                    coordinator_access__can_modify_jobs=True
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class JobTypeAdmin(PolymorphicInlineSupportMixin, OverrideFieldQuerySetMixin, RichTextAdmin, JobTypeBaseAdmin):
    fields = ('name', 'displayed_name', 'activityarea', 'location', 'default_duration', 'description', 'visible')
    list_display = ['__str__', 'default_duration', 'location', 'contacts_text', 'visible', 'last_used']
    list_filter = (('activityarea', admin.RelatedOnlyFieldListFilter), 'visible')
    autocomplete_fields = ['activityarea', 'location']
    search_fields = ['name', 'displayed_name', 'activityarea__name', 'last_used']
    actions = ['transform_job_type', 'action_hide', 'action_make_visible']
    inlines = [ContactInlineForJob, JobExtraInlineForJobType]

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
            # convert all jobs of this type
            for recurring_job in inst.recuringjob_set.all():
                recurring_job.convert()
            # delete type
            inst.job_extras_set.all().delete()
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
        qs = super().get_queryset(request)
        if request.resolver_match.view_name == 'admin:autocomplete':
            qs = qs.filter(visible=True)
        else:
            qs = qs.annotate(last_used=Max('recuringjob__time'))
        return qs

    def get_search_fields(self, request):
        search_fields = [*super().get_search_fields(request)]
        if request.resolver_match.view_name == 'admin:autocomplete':
            search_fields.remove('last_used')
        return search_fields
