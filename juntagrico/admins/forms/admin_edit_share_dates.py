from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.utils import timezone
from django.utils.translation import gettext as _

field_choices = [('paid_date', _('Bezahlt am')),
                 ('issue_date', _('Ausgestellt am')),
                 ('booking_date', _('Eingebucht am')),
                 ('cancelled_date', _('Gekündigt am')),
                 ('termination_date', _('Gekündigt auf')),
                 ('payback_date', _('Zurückbezahlt am'))]


class EditShareDatesForm(forms.Form):
    target_field = forms.CharField(label='', widget=forms.Select(choices=field_choices))
    date = forms.DateField(label='', widget=AdminDateWidget(), initial=timezone.now().date())
    overwrite = forms.BooleanField(label=_('Überschreiben?'), required=False)
    note = forms.CharField(label=_('Notiz anfügen'), required=False)
