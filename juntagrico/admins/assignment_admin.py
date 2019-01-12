from django.contrib import admin

from juntagrico.dao.jobdao import JobDao
from juntagrico.util.addons import get_assignment_inlines


class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'member',
                    'job']
    search_fields = ['member__first_name', 'member__last_name']
    raw_id_fields = ['member', 'job']
    inlines = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_assignment_inlines())
        super(AssignmentAdmin, self).__init__(*args, **kwargs)

    def get_queryset(self, request):
        qs = super(admin.ModelAdmin, self).get_queryset(request)
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            return qs.filter(job__id__in=JobDao.ids_for_area_by_contact(request.user.member))
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'job' and request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            kwargs['queryset'] = JobDao.jobs_by_ids(
                JobDao.ids_for_area_by_contact(request.user.member))
        return super(admin.ModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
