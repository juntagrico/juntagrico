from django.contrib import admin

from juntagrico.util.addons import get_share_inlines


class ShareAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'member', 'number', 'paid_date', 'issue_date', 'booking_date', 'cancelled_date',
                    'termination_date', 'payback_date']
    search_fields = ['id', 'member__email', 'member__first_name', 'member__last_name', 'number', 'paid_date',
                     'issue_date', 'booking_date', 'cancelled_date', 'termination_date', 'payback_date']
    raw_id_fields = ['member']
    inlines = []

    def __init__(self, *args, **kwargs):
        self.inlines.extend(get_share_inlines())
        super(ShareAdmin, self).__init__(*args, **kwargs)
