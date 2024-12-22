from django.contrib import admin
from django.utils.translation import gettext as _

from juntagrico.admins import RichTextAdmin


class SubscriptionSizeAdmin(RichTextAdmin):
    list_display = ['__str__', 'units', 'category', 'orderable', 'product', 'depot_list']
    autocomplete_fields = ['category', 'product']
    search_fields = ['name', 'long_name', 'description', 'category__name', 'product__name']

    @admin.display(
        boolean=True,
        ordering='category',
        description=_('Bestellbar')
    )
    def orderable(self, obj):
        return obj.category is not None
