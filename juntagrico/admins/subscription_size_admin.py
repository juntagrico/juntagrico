from juntagrico.admins import RichTextAdmin


class SubscriptionSizeAdmin(RichTextAdmin):
    list_display = ['__str__', 'units', 'product', 'visible', 'depot_list']
    autocomplete_fields = ['product']
    search_fields = ['name', 'long_name', 'product__name']
