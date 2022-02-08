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
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'visible')
        }),
        (_('Adresse'), {
            'description': _('Wenn Adresse nicht leer ist, wird ein Link zur Wegbeschreibung angezeigt.'),
            'fields': ('addr_street', ('addr_zipcode', 'addr_location')),
        }),
        (_('Koordinaten'), {
            'description': _('Wenn Koordinaten nicht leer sind, wird eine Karte eingeblendet '
                             'und ein Link zur Wegbeschreibung angezeigt.'),
            'fields': (('latitude', 'longitude'),),
        }),
    )

    @admin.action(description=_('Ausgewählte Orte ersetzen'))
    def replace(self, request, queryset):
        if 'apply' in request.POST:
            form = LocationReplaceForm(queryset, request.POST)
            if form.is_valid():
                form.save()
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
