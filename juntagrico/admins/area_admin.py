from adminsortable2.admin import SortableAdminMixin, SortableTabularInline
from django.utils.safestring import mark_safe
from polymorphic.admin import PolymorphicInlineSupportMixin
from django.utils.translation import gettext as _
from django.contrib import admin

from juntagrico.admins import RichTextAdmin, AreaCoordinatorMixin
from juntagrico.admins.inlines.contact_inline import ContactInline
from juntagrico.entity.jobs import AreaCoordinator


class AreaCoordinatorInline(SortableTabularInline):
    model = AreaCoordinator
    autocomplete_fields = ('member',)
    min_num = 1
    extra = 0

    def get_formset(self, *args, **kwargs):
        # validates, that at least min_num undeleted forms are sent
        return super().get_formset(*args, validate_min=True, **kwargs)

    def has_delete_permission(self, request, obj=None):
        # only show delete option of there is more than 1 coordinator
        return obj is not None and obj.coordinators.count() > 1


class AreaAdmin(PolymorphicInlineSupportMixin, SortableAdminMixin, AreaCoordinatorMixin, RichTextAdmin):
    filter_horizontal = ['members']
    raw_id_fields = ['coordinator']
    list_display = ['name', 'core', 'hidden', 'coordinator', 'auto_add_new_members', 'contacts_text']
    search_fields = ['name']
    inlines = [AreaCoordinatorInline, ContactInline]
    coordinator_permissions = ['view']

    @admin.display(description=_('Kontakt'))
    def contacts_text(self, instance):
        return mark_safe("<br>".join([str(c) for c in instance.contacts]))

    def get_fields(self, request, obj=None):
        if super(AreaCoordinatorMixin, self).has_view_permission(request):
            return super().get_fields(request, obj)
        else:
            # limited access for area coordinators
            return ['name', 'description']
