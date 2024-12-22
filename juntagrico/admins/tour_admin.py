from adminsortable2.admin import SortableAdminMixin, SortableTabularInline

from juntagrico.admins import RichTextAdmin
from juntagrico.entity.depot import Depot


class DepotInline(SortableTabularInline):
    model = Depot
    fields = ['name']
    readonly_fields = ['name']
    extra = 0
    max_num = 0
    can_delete = False


class TourAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['name', 'visible_on_list']
    search_fields = ['name', 'description', 'depots__name']
    inlines = [DepotInline]
