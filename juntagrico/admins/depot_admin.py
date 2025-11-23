from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin, SortableTabularInline
from django.utils.safestring import mark_safe

from juntagrico.admins.inlines.depot_subscriptiontype_inline import DepotSubscriptionTypeInline
from juntagrico.entity.depot import DepotCoordinator
from polymorphic.admin import PolymorphicInlineSupportMixin
from django.utils.translation import gettext as _
from juntagrico.admins import RichTextAdmin, DepotCoordinatorMixin, DepotCoordinatorInlineMixin


class DepotCoordinatorInline(DepotCoordinatorInlineMixin, SortableTabularInline):
    model = DepotCoordinator
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


class DepotAdmin(PolymorphicInlineSupportMixin, SortableAdminMixin, DepotCoordinatorMixin, RichTextAdmin):
    autocomplete_fields = ['location']
    list_display = ['name', 'tour', 'weekday', 'fee', 'visible', 'depot_list']
    exclude = ['capacity']
    search_fields = ['name', 'description', 'access_information', 'location__name', 'location__addr_street',
                     'location__addr_zipcode', 'location__addr_location', 'tour__name', 'fee',
                     'coordinators__first_name', 'coordinators__last_name']
    inlines = [DepotSubscriptionTypeInline, DepotCoordinatorInline]
    list_filter = (('tour', admin.RelatedOnlyFieldListFilter), 'visible', 'depot_list', 'tour__visible_on_list')
    coordinator_access = 'can_modify_depot'
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
            # limited access for depot coordinators
            return ['name', 'description', 'access_information']

    def get_readonly_fields(self, request, obj=None):
        if self.has_full_view_permission(request):
            return super().get_readonly_fields(request, obj)
        else:
            # limited access for depot coordinators
            return ['name']
