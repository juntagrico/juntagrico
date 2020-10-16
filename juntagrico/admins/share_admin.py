from django.utils import timezone
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.http import HttpResponseRedirect

from juntagrico.admins import BaseAdmin
from juntagrico.config import Config
from juntagrico.admins.forms.admin_mark_share import MarkShareOptionsForm


class ShareAdmin(BaseAdmin):
    list_display = ['__str__', 'member', 'number', 'paid_date', 'issue_date', 'booking_date', 'cancelled_date',
                    'termination_date', 'payback_date']
    search_fields = ['id', 'member__email', 'member__first_name', 'member__last_name', 'number', 'paid_date',
                     'issue_date', 'booking_date', 'cancelled_date', 'termination_date', 'payback_date']
    raw_id_fields = ['member']
    actions = ['mark_share']

    def mark_share(self, request, queryset):
        if 'apply' in request.POST:
            form = MarkShareOptionsForm(request.POST)
            if form.is_valid():
                target_field = form.cleaned_data['target_field']
                date = form.cleaned_data['date']
                overwrite = form.cleaned_data['overwrite']
                input_count = queryset.count()
                if not overwrite:
                    queryset = queryset.filter(**{target_field: None})
                filter_count = queryset.count()
                queryset.update(**{target_field: date})
                self.message_user(request, _('{} von {} {} bearbeitet').format(filter_count, input_count, Config.vocabulary('share_pl')))
                return HttpResponseRedirect(request.get_full_path())
        elif 'cancel' in request.POST:
            return HttpResponseRedirect(request.get_full_path())
        else:
            form = MarkShareOptionsForm()

        return render(request,
                      'admin/mark_share_intermediate.html',
                      context={
                          'shares': queryset,
                          'form': form,
                      })

    mark_share.short_description = _('Ausgewählte {} bearbeiten').format(Config.vocabulary('share_pl'))
