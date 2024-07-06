from django import forms
from django.utils.translation import gettext as _

from juntagrico.entity.location import Location


class LocationReplaceForm(forms.Form):
    replace_by = forms.ModelChoiceField(Location.objects.all(), label=_('Ersetzen mit'))

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = queryset
        self.fields['replace_by'].queryset = Location.objects.exclude(pk__in=queryset)

    def save(self, commit=True):
        replace_by = self.cleaned_data['replace_by']
        # the generic ways to get the related fields with django.contrib.admin.utils.NestedObjects
        # or location._meta.get_fields seem less robust and harder to maintain.
        related = ['jobtype_set', 'onetimejob_set']
        for location in self.queryset:
            for related_field in related:
                for related_object in getattr(location, related_field).all():
                    related_object.location = replace_by
                    related_object.save()
        # delete replaced locations
        self.queryset.delete()
