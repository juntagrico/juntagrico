from adminsortable2.admin import SortableAdminMixin, SortableTabularInline
from django.utils.safestring import mark_safe
from polymorphic.admin import PolymorphicInlineSupportMixin
from django.utils.translation import gettext as _
from django.contrib import admin

from juntagrico.admins import RichTextAdmin, AreaCoordinatorMixin, AreaCoordinatorInlineMixin
from juntagrico.admins.inlines.contact_inline import ContactInline
from juntagrico.entity.jobs import AreaCoordinator


class AreaCoordinatorInline(AreaCoordinatorInlineMixin, SortableTabularInline):
    model = AreaCoordinator
    autocomplete_fields = ('member',)
    min_num = 1
    extra = 0
    coordinator_permissions = ['view']

    def get_formset(self, *args, **kwargs):
        # validates, that at least min_num undeleted forms are sent
        return super().get_formset(*args, validate_min=True, **kwargs)

    def has_delete_permission(self, request, obj=None):
        # only show delete option of there is more than 1 coordinator
        return super().has_delete_permission(request, obj) and obj is not None and obj.coordinators.count() > 1


class AreaAdmin(PolymorphicInlineSupportMixin, SortableAdminMixin, AreaCoordinatorMixin, RichTextAdmin):
    filter_horizontal = ['members']
    list_display = ['name', 'core', 'hidden', 'coordinators_text', 'auto_add_new_members', 'contacts_text']
    search_fields = ['name', 'description', 'coordinators__first_name', 'coordinators__last_name']
    inlines = [AreaCoordinatorInline, ContactInline]
    coordinator_permissions = ['view', 'change']

    @admin.display(description=_('Kontakt'))
    def contacts_text(self, instance):
        return mark_safe("<br>".join([str(c) for c in instance.contacts]))

    @admin.display(description=_('Koordination'))
    def coordinators_text(self, instance):
        return mark_safe("<br>".join([str(c) for c in instance.coordinators.all()]))

    def get_fields(self, request, obj=None):
        if self.has_full_view_permission(request):
            return super().get_fields(request, obj)
        else:
            # limited access for area coordinators
            return ['name', 'description']

    def get_readonly_fields(self, request, obj=None):
        if self.has_full_view_permission(request):
            return super().get_readonly_fields(request, obj)
        else:
            # limited access for area coordinators
            return ['name']
