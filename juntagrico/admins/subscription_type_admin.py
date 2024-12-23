from adminsortable2.admin import SortableAdminMixin
from django.contrib.admin import RelatedOnlyFieldListFilter, TabularInline

from juntagrico.admins import RichTextAdmin
from juntagrico.admins.inlines.depot_subscriptiontype_inline import DepotSubscriptionTypeInline
from juntagrico.config import Config
from juntagrico.entity.subtypes import SubscriptionBundle


class SubscriptionTypeAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['__str__', 'price', 'required_assignments',
                    'required_core_assignments', 'visible']
    exclude = ['trial']
    inlines = [DepotSubscriptionTypeInline]
    search_fields = ['name', 'long_name', 'size__name', 'size__long_name', 'size__products__name']
    autocomplete_fields = ['size']
    list_filter = ['visible',
                   ('size', RelatedOnlyFieldListFilter),
                   ('size__category', RelatedOnlyFieldListFilter)]

    def get_exclude(self, request, obj=None):
        if not Config.enable_shares():
            return ['shares'] if self.exclude is None else self.exclude.append('shares')
        return self.exclude


if Config.enable_shares():
    SubscriptionTypeAdmin.list_display.insert(2, 'shares')
    SubscriptionTypeAdmin.list_filter.insert(1, 'shares')


class SubscriptionBundleInline(TabularInline):
    model = SubscriptionBundle
    fields = ['name', 'long_name']
    extra = 0
    max_num = 0
    show_change_link = True
    can_delete = False


class SubscriptionCategoryAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['__str__']
    search_fields = ['name', 'description']
    inlines = [SubscriptionBundleInline]
