from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.db.models import Q


class JuntagricoAdminSite(admin.AdminSite):
    def has_permission(self, request):
        # give area coordinators access to admin
        return request.user.is_active and (
            request.user.is_staff or request.user.member.area_access.filter(
                Q(can_modify_area=True) | Q(can_modify_jobs=True) | Q(can_modify_assignments=True)
            ).exists() or request.user.member.depot_access.filter(can_modify_depot=True).exists()
        )


class JuntagricoAdminConfig(AdminConfig):
    default_site = 'juntagrico.admin_sites.JuntagricoAdminSite'
