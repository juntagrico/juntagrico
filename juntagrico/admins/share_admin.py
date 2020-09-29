from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.admins import BaseAdmin
from juntagrico.config import Config


class ShareAdmin(BaseAdmin):
    list_display = ['__str__', 'member', 'number', 'paid_date', 'issue_date', 'booking_date', 'cancelled_date',
                    'termination_date', 'payback_date']
    search_fields = ['id', 'member__email', 'member__first_name', 'member__last_name', 'number', 'paid_date',
                     'issue_date', 'booking_date', 'cancelled_date', 'termination_date', 'payback_date']
    raw_id_fields = ['member']
    actions = ['mark_paid']

    def mark_paid(self, request, queryset):
        for share in queryset.all():
            share.paid_date = share.paid_date or timezone.now().date()
            share.save()

    mark_paid.short_description = _('ausgewählte {} als bezahlt eintragen').format(Config.vocabulary('share_pl'))
