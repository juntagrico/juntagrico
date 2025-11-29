from adminsortable2.admin import SortableAdminMixin

from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter, TabularInline
from django.utils.translation import gettext as _

from juntagrico.admins import RichTextAdmin
from juntagrico.admins.inlines.depot_subscriptiontype_inline import DepotSubscriptionTypeInline
from juntagrico.config import Config
from juntagrico.entity.subtypes import SubscriptionBundle, ProductSize


class SubscriptionTypeAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['__str__', 'price', 'required_assignments',
                    'required_core_assignments', 'visible', 'is_extra']
    exclude = ['trial']
    inlines = [DepotSubscriptionTypeInline]
    search_fields = ['name', 'long_name', 'bundle__name', 'bundle__long_name', 'bundle__products__name']
    autocomplete_fields = ['bundle']
    list_filter = ['visible',
                   ('bundle', RelatedOnlyFieldListFilter),
                   ('bundle__category', RelatedOnlyFieldListFilter)]

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


class ProductSizeInline(TabularInline):
    model = ProductSize
    fields = ['name', 'product', 'units', 'show_in_depot_list']


class SubscriptionBundleAdmin(RichTextAdmin):
    list_display = ['long_name', 'category', 'orderable']
    autocomplete_fields = ['category']
    search_fields = ['long_name', 'description', 'category__name', 'products__name']
    inlines = [ProductSizeInline]

    @admin.display(
        boolean=True,
        ordering='category',
        description=_('Bestellbar')
    )
    def orderable(self, obj):
        return obj.category is not None
