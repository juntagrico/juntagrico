from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from juntagrico.config import Config


class UserAdmin(auth_admin.UserAdmin):
    list_display = ('username', 'member', 'member__email', 'has_permissions', 'in_group', 'is_staff', )
    search_fields = ('username', 'member__first_name', 'member__last_name', 'member__email')
    readonly_fields = ('member',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        fieldsets[1] = (Config.vocabulary('member'), {'fields': ('member',)})
        return fieldsets

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match.view_name != 'admin:autocomplete':
            qs = qs.annotate(has_group=Count('groups'), has_permission=Count('user_permissions'))
        return qs

    @admin.display(
        boolean=True,
        ordering='-has_group',
        description=_('In Gruppe')
    )
    def in_group(self, instance):
        return instance.groups.exists()

    @admin.display(
        boolean=True,
        ordering='-has_permission',
        description=_('Hat Berechtigungen')
    )
    def has_permissions(self, instance):
        return instance.user_permissions.exists()
