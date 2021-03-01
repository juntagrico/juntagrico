from juntagrico.admins import BaseAdmin
from adminsortable2.admin import SortableAdminMixin


class ExtraSubscriptionTypeAdmin(SortableAdminMixin, BaseAdmin):
    list_display = ['name', 'category', 'size', 'visible', 'depot_list']
    exclude = []


class ExtraSubscriptionCategoryAdmin(SortableAdminMixin, BaseAdmin):
    list_display = ['name', 'visible', 'depot_list']
    exclude = []
