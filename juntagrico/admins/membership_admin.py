from import_export.admin import ExportMixin

from juntagrico.admins import BaseAdmin
from juntagrico.resources.membership import MembershipResource


class MembershipAdmin(ExportMixin, BaseAdmin):
    fields = ('account', 'number', 'creation_date', 'activation_date', 'cancellation_date', 'deactivation_date', 'notes')
    readonly_fields = ['creation_date']
    list_display = ['__str__', 'account', 'number',
                    'creation_date', 'activation_date', 'cancellation_date', 'deactivation_date']
    search_fields = ['account__first_name', 'account__last_name', 'number', 'creation_date',
                     'activation_date', 'cancellation_date', 'deactivation_date']
    autocomplete_fields = ['account']
    resource_classes = [MembershipResource]
