import datetime

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.timezone import get_default_timezone as gdtz, localtime, is_naive
from django.utils.translation import gettext as _
from djrichtextfield.widgets import RichTextWidget

from juntagrico.entity.jobs import RecuringJob
from juntagrico.util.temporal import weekday_choices


class JobCopyForm(forms.ModelForm):
    class Meta:
        model = RecuringJob
        fields = ['type', 'slots', 'infinite_slots', 'duration_override', 'multiplier', 'additional_description']

    weekdays = forms.MultipleChoiceField(label=_('Wochentage'), choices=weekday_choices,
                                         widget=forms.widgets.CheckboxSelectMultiple)

    time = forms.TimeField(label=_('Zeit'), required=True,
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
            self.fields['time'].initial = inst.time.astimezone(gdtz())
        else:
            self.fields['time'].initial = localtime(inst.time)
        self.fields['weekdays'].initial = [inst.time.isoweekday()]

        if 'djrichtextfield' in settings.INSTALLED_APPS and hasattr(settings, 'DJRICHTEXTFIELD_CONFIG'):
            self.fields['additional_description'].widget = RichTextWidget()

        self.new_jobs = []

    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned(cleaned_data) and not self.get_datetimes(cleaned_data):
            raise ValidationError(_('Kein neuer Job fällt zwischen Anfangs- und Enddatum'), code='no_job_in_range')
        return cleaned_data

    def save(self, commit=True):
        inst = self.instance

        newjob = None
        for dt in self.get_datetimes(self.cleaned_data):
            newjob = RecuringJob(
                type=inst.type,
                slots=inst.slots,
                infinite_slots=inst.infinite_slots,
                time=dt,
                multiplier=inst.multiplier,
                additional_description=inst.additional_description,
                duration_override=inst.duration_override,
            )
            if commit:
                newjob.save()
            self.new_jobs.append(newjob)
        return newjob

    def save_related(self, formsets):
        # collect contacts from formsets
        contacts = []
        if formsets and len(formsets) >= 1:
            for contact_form in formsets[0].forms:
                if not contact_form.cleaned_data['DELETE']:
                    contacts.append(contact_form.instance.copy())
            # excepted by ModelAdmin
            formsets[0].new_objects = []
            formsets[0].changed_objects = []
            formsets[0].deleted_objects = []
        # save and apply contacts
        for job in self.new_jobs:
            job.save()
            for contact in contacts:
                job.contact_set.add(contact, bulk=False)

    @staticmethod
    def cleaned(cleaned_data):
        return all(k in cleaned_data for k in ('start_date', 'end_date', 'weekdays', 'weekly', 'time'))

    @staticmethod
    def get_datetimes(cleaned_data):
        start = cleaned_data['start_date']
        end = cleaned_data['end_date']
        time = cleaned_data['time']
        weekdays = cleaned_data['weekdays']
        weekdays = set(int(i) for i in weekdays)
        skip_even_weeks = cleaned_data['weekly'] == '14'
        res = []
        for delta in range((end - start).days + 1):
            if skip_even_weeks and delta % 14 >= 7:
                continue
            date = start + datetime.timedelta(delta)
            if date.isoweekday() not in weekdays:
                continue
            dt = datetime.datetime.combine(date, time)
            if settings.USE_TZ and is_naive(dt):
                dt = dt.astimezone(gdtz())
            res.append(dt)
        return res


class JobCopyToFutureForm(JobCopyForm):
    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned(cleaned_data) and self.get_datetimes(cleaned_data)[0] <= timezone.now():
            raise ValidationError(_('Neue Jobs können nicht in der Vergangenheit liegen.'), code='date_in_past')
        return cleaned_data
