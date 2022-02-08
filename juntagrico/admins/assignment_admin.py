from juntagrico.admins import BaseAdmin
from juntagrico.dao.jobdao import JobDao
from juntagrico.util.admin import formfield_for_coordinator


class AssignmentAdmin(BaseAdmin):
    list_display = ['__str__', 'member', 'time', 'amount', 'job']
    search_fields = ['member__first_name', 'member__last_name']
    raw_id_fields = ['member', 'job']

    def has_change_permission(self, request, obj=None):
        return (obj is None or obj.can_modify(request)) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return (obj is None or obj.can_modify(request)) and super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            return qs.filter(job__id__in=JobDao.ids_for_area_by_contact(request.user.member))
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs = formfield_for_coordinator(request,
                                           db_field.name,
                                           'job',
                                           'juntagrico.is_area_admin',
                                           JobDao.for_area_by_contact)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
