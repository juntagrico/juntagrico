from juntagrico.admins import BaseAdmin


class BillingPeriodAdmin(BaseAdmin):
    list_display = ['type']
    autocomplete_fields = ['type']
