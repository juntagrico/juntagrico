from django.db.models import Q

from juntagrico.admins import BaseAdmin, AreaCoordinatorMixin, can_see_all
from juntagrico.entity.jobs import Job


def get_allowed_jobs(member):
    allowed_areas = member.coordinated_areas.filter(coordinator_access__can_modify_assignments=True)
    return Job.objects.filter(
        Q(OneTimeJob___activityarea__in=allowed_areas) |
        Q(RecuringJob___type__activityarea__in=allowed_areas)
    )


class AssignmentAdmin(AreaCoordinatorMixin, BaseAdmin):
    list_display = ['__str__', 'member', 'time', 'amount', 'job']
    search_fields = ['member__first_name', 'member__last_name']
    date_hierarchy = 'job__time'
    raw_id_fields = ['member', 'job']
    coordinator_access = 'can_modify_assignments'

    def get_area(self, obj):
        return obj.job.get_real_instance().type.activityarea

    def has_change_permission(self, request, obj=None):
        return (obj is None or obj.can_modify(request)) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return (obj is None or obj.can_modify(request)) and super().has_delete_permission(request, obj)

    def get_coordinator_queryset(self, request, qs):
        return qs.filter(job__id__in=get_allowed_jobs(request.user.member))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # used for form validation
        if db_field.name == 'job':
            user = request.user
            if not can_see_all(user, 'job'):
                kwargs["queryset"] = get_allowed_jobs(user.member)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
