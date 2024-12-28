from django.contrib import admin
from django.contrib.admin import TabularInline
from django.utils.translation import gettext as _

from juntagrico.admins import RichTextAdmin
from juntagrico.entity.subtypes import SubscriptionItem


class SubscriptionItemInline(TabularInline):
    model = SubscriptionItem
    fields = ['product', 'units']


class SubscriptionSizeAdmin(RichTextAdmin):
    list_display = ['name', 'long_name', 'category', 'orderable']
    autocomplete_fields = ['category']
    search_fields = ['name', 'long_name', 'description', 'category__name', 'products__name']
    inlines = [SubscriptionItemInline]

    @admin.display(
        boolean=True,
        ordering='category',
        description=_('Bestellbar')
    )
    def orderable(self, obj):
        return obj.category is not None
