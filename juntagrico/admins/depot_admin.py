from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from juntagrico.admins import RichTextAdmin


class DepotAdmin(SortableAdminMixin, RichTextAdmin):
    raw_id_fields = ['contact']
    autocomplete_fields = ['location']
    list_display = ['name', 'tour', 'weekday', 'contact', 'visible', 'depot_list']
    exclude = ['capacity']
    search_fields = ['name', 'location__name', 'location__addr_street', 'location__addr_zipcode', 'location__addr_location', 'tour__name']
    list_filter = (('tour', admin.RelatedOnlyFieldListFilter), 'visible', 'depot_list', 'tour__visible_on_list')
