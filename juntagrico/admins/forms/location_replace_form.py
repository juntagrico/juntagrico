from django import forms
from django.utils.translation import gettext as _

from juntagrico.entity.location import Location


class LocationReplaceForm(forms.Form):
    replace_by = forms.ModelChoiceField(Location.objects.all(), label=_('Ersetzen mit'))

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['replace_by'].queryset = Location.objects.exclude(pk__in=queryset)
