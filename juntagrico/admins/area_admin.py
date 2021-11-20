from adminsortable2.admin import SortableAdminMixin
from polymorphic.admin import PolymorphicInlineSupportMixin

from juntagrico.admins import RichTextAdmin
from juntagrico.admins.inlines.contact_inline import ContactInline
from juntagrico.util.admin import queryset_for_coordinator


class AreaAdmin(PolymorphicInlineSupportMixin, SortableAdminMixin, RichTextAdmin):
    filter_horizontal = ['members']
    raw_id_fields = ['coordinator']
    list_display = ['name', 'core', 'hidden', 'coordinator', 'get_email', 'auto_add_new_members']
    list_display = ['name', 'core', 'hidden', 'coordinator', 'get_email']
    inlines = [ContactInline]

    def get_queryset(self, request):
        return queryset_for_coordinator(self, request, 'coordinator')

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('juntagrico.is_area_admin') and (
                not (request.user.is_superuser or request.user.has_perm('juntagrico.is_operations_group'))):
            return ['name', 'core', 'hidden', 'coordinator']
        return self.readonly_fields
