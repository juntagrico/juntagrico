from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _

from juntagrico.admins import BaseAdmin
from juntagrico.admins.forms.admin_edit_share_dates import EditShareDatesForm
from juntagrico.config import Config


class ShareAdmin(BaseAdmin):
    fields = ('member', 'value', 'creation_date', 'paid_date', 'issue_date', 'booking_date', 'cancelled_date',
              'termination_date', 'payback_date', 'number', 'sent_back', 'reason_for_acquisition', 'reason_for_cancellation', 'notes')
    readonly_fields = ['creation_date']
    list_display = ['__str__', 'member', 'number', 'value', 'paid_date', 'issue_date', 'booking_date', 'cancelled_date',
                    'termination_date', 'payback_date']
    search_fields = ['id', 'member__email', 'member__first_name', 'member__last_name', 'number', 'value', 'paid_date',
                     'issue_date', 'booking_date', 'cancelled_date', 'termination_date', 'payback_date']
    raw_id_fields = ['member']
    actions = ['mass_edit_share_dates']

    @admin.action(description=_('Datum für ausgewählte {} setzen').format(Config.vocabulary('share_pl')))
    def mass_edit_share_dates(self, request, queryset):
        if 'apply' in request.POST:
            form = EditShareDatesForm(request.POST)
            if form.is_valid():
                target_field = form.cleaned_data['target_field']
                date = form.cleaned_data['date']
                overwrite = form.cleaned_data['overwrite']
                input_count = queryset.count()
                if not overwrite:
                    queryset = queryset.filter(**{target_field: None})
                filter_count = queryset.count()
                # add note before setting date as queryset may be empty afterward due to applied filters
                additional_note = form.cleaned_data['note']
                if additional_note:
                    for share in queryset:
                        share.notes += ('\n' if share.notes else '') + additional_note
                        share.save()
                # update dates
                queryset.update(**{target_field: date})
                self.message_user(request, _('{} von {} {} bearbeitet').format(filter_count, input_count, Config.vocabulary('share_pl')))
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = EditShareDatesForm()

        return render(request,
                      'admin/mass_edit_share_dates_intermediate.html',
                      context=dict(
                          self.admin_site.each_context(request),
                          title=_('Mehrere Anteilscheindaten bearbeiten'),
                          shares=queryset,
                          form=form
                      ))
