from adminsortable2.admin import SortableAdminMixin, SortableStackedInline, SortableTabularInline

from django.contrib import admin
from django.utils.translation import gettext as _

from juntagrico.admins import RichTextAdmin
from juntagrico.admins.inlines.depot_subscriptiontype_inline import DepotSubscriptionTypeInline
from juntagrico.config import Config
from juntagrico.entity.subtypes import SubscriptionBundle, SubscriptionBundleProductSize, SubscriptionType


class SubscriptionTypeAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['__str__', 'price', 'required_assignments',
                    'required_core_assignments', 'visible', 'is_extra']
    exclude = ['trial']
    inlines = [DepotSubscriptionTypeInline]
    search_fields = ['name', 'long_name', 'bundle__name', 'bundle__long_name', 'bundle__products__name']
    autocomplete_fields = ['bundle']
    list_filter = ['visible',
                   ('bundle', admin.RelatedOnlyFieldListFilter),
                   ('bundle__category', admin.RelatedOnlyFieldListFilter)]

    def get_exclude(self, request, obj=None):
        exclude = super().get_exclude(request, obj)
        if not Config.enable_shares():
            exclude.append('shares')
        return exclude


if Config.enable_shares():
    SubscriptionTypeAdmin.list_display.insert(2, 'shares')
    SubscriptionTypeAdmin.list_filter.insert(1, 'shares')


class SubscriptionBundleInline(SortableTabularInline):
    model = SubscriptionBundle
    fields = ['long_name']
    extra = 0
    max_num = 0
    show_change_link = True
    can_delete = False


class SubscriptionCategoryAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['__str__']
    search_fields = ['name', 'description']
    inlines = [SubscriptionBundleInline]


class ProductSizeInline(admin.TabularInline):
    model = SubscriptionBundleProductSize
    extra = 1


class SubscriptionTypeInline(SortableStackedInline):
    model = SubscriptionType
    extra = 0
    fieldsets = [
        (
            None,
            {
                'fields': [
                    ('name', 'long_name'),
                    'description',
                    ('price', 'shares', 'required_assignments', 'required_core_assignments'),
                    ('visible', 'is_extra', 'trial_days'),
                    ('interval', 'offset')
                ],
            },
        ),
    ]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not Config.enable_shares():
            fieldsets[0][1]['fields'][2] = ('price', 'required_assignments', 'required_core_assignments')
        return fieldsets

    def get_exclude(self, request, obj=None):
        exclude = super().get_exclude(request, obj) or []
        if not Config.enable_shares():
            exclude.append('shares')
        return exclude


class SubscriptionBundleAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['long_name', 'category', 'orderable']
    autocomplete_fields = ['category']
    search_fields = ['long_name', 'description', 'category__name', 'product_sizes__name']
    inlines = [ProductSizeInline, SubscriptionTypeInline]

    @admin.display(
        boolean=True,
        ordering='category',
        description=_('Bestellbar')
    )
    def orderable(self, obj):
        return obj.category is not None
