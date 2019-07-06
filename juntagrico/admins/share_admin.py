from juntagrico.admins import BaseAdmin


class ShareAdmin(BaseAdmin):
    list_display = ['__str__', 'member', 'number', 'paid_date', 'issue_date', 'booking_date', 'cancelled_date',
                    'termination_date', 'payback_date']
    search_fields = ['id', 'member__email', 'member__first_name', 'member__last_name', 'number', 'paid_date',
                     'issue_date', 'booking_date', 'cancelled_date', 'termination_date', 'payback_date']
    raw_id_fields = ['member']
