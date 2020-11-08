import datetime

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.timezone import get_default_timezone as gdtz, localtime, is_naive
from django.utils.translation import gettext as _

from juntagrico.entity.jobs import RecuringJob
from juntagrico.util.temporal import weekday_choices


class JobCopyForm(forms.ModelForm):
    class Meta:
        model = RecuringJob
        fields = ['type', 'slots', 'infinite_slots']

    weekdays = forms.MultipleChoiceField(label=_('Wochentage'), choices=weekday_choices,
                                         widget=forms.widgets.CheckboxSelectMultiple)

    time = forms.TimeField(label=_('Zeit'), required=False,
                           widget=admin.widgets.AdminTimeWidget)

    start_date = forms.DateField(label=_('Anfangsdatum'), required=True,
                                 widget=admin.widgets.AdminDateWidget)
    end_date = forms.DateField(label=_('Enddatum'), required=True,
                               widget=admin.widgets.AdminDateWidget)

    weekly = forms.ChoiceField(choices=[(7, _('jede Woche')), (14, _('Alle zwei Wochen'))],
                               widget=forms.widgets.RadioSelect, initial=7)

    def __init__(self, *a, **k):
        super(JobCopyForm, self).__init__(*a, **k)
        inst = k.pop('instance')

        self.fields['start_date'].initial = inst.time.date() + \
            datetime.timedelta(days=1)
        if is_naive(inst.time):
            self.fields['time'].initial = gdtz().localize(inst.time)
        else:
            self.fields['time'].initial = localtime(inst.time)
        self.fields['weekdays'].initial = [inst.time.isoweekday()]

    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        if 'start_date' in cleaned_data and 'end_date' in cleaned_data:
            if not self.get_dates(cleaned_data):
                raise ValidationError(
                    _('Kein neuer Job fällt zwischen Anfangs- und Enddatum'))
        return cleaned_data

    def save(self, commit=True):
        time = self.cleaned_data['time']

        inst = self.instance

        newjob = None
        for date in self.get_dates(self.cleaned_data):
            dt = datetime.datetime.combine(date, time)
            if is_naive(dt):
                dt = gdtz().localize(dt)
            newjob = RecuringJob.objects.create(
                type=inst.type, slots=inst.slots, infinite_slots=inst.infinite_slots, time=dt)
            newjob.save()
        return newjob

    def save_m2m(self):
        # HACK: the admin expects this method to exist
        pass

    @staticmethod
    def get_dates(cleaned_data):
        start = cleaned_data['start_date']
        end = cleaned_data['end_date']
        weekdays = cleaned_data['weekdays']
        weekdays = set(int(i) for i in weekdays)
        res = []
        skip_even_weeks = cleaned_data['weekly'] == '14'
        for delta in range((end - start).days + 1):
            if skip_even_weeks and delta % 14 >= 7:
                continue
            date = start + datetime.timedelta(delta)
            if not date.isoweekday() in weekdays:
                continue
            res.append(date)
        return res
