from adminsortable2.admin import SortableAdminMixin

from juntagrico.admins import RichTextAdmin
from juntagrico.config import Config


class SubscriptionTypeAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['__str__', 'price', 'required_assignments',
                    'required_core_assignments', 'visible']
    exclude = ['trial']
    search_fields = ['name', 'long_name', 'size__name', 'size__long_name', 'size__product__name']
    autocomplete_fields = ['size']

    def get_exclude(self, request, obj=None):
        if not Config.enable_shares():
            return ['shares'] if self.exclude is None else self.exclude.append('shares')
        return self.exclude


if Config.enable_shares():
    SubscriptionTypeAdmin.list_display.insert(2, 'shares')
