from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _

from juntagrico.admins import RichTextAdmin
from juntagrico.admins.forms.location_replace_form import LocationReplaceForm


class LocationAdmin(SortableAdminMixin, RichTextAdmin):
    list_display = ['name', 'addr_street', 'addr_zipcode', 'addr_location', 'latitude', 'longitude', 'visible']
    actions = ['replace']

    @admin.action(description=_('Ausgewählte Orte ersetzen'))
    def replace(self, request, queryset):
        if 'apply' in request.POST:
            form = LocationReplaceForm(queryset, request.POST)
            if form.is_valid():
                replace_by = form.cleaned_data['replace_by']
                # TODO: replace elements from queryset in all places they are used and them delete them.
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = LocationReplaceForm(queryset)

        return render(request,
                      'admin/replace_location_intermediate.html',
                      context=dict(
                          self.admin_site.each_context(request),
                          title=_('Orte Ersetzen'),
                          locations=queryset,
                          form=form
                      ))
