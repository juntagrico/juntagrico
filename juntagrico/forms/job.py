from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, HTML
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import Form, ChoiceField, CharField, Textarea, BooleanField, ModelChoiceField
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_lazy
from django_select2.forms import ModelSelect2Widget

from juntagrico.config import Config
from juntagrico.entity.jobs import JobExtra, Assignment, Job, JobType
from juntagrico.entity.member import Member
from juntagrico.signals import subscribed, assignment_changed


class JobSubscribeForm(Form):
    MAX_VALUE = 15
    UNSUBSCRIBE = 'unsubscribe'

    slots = ChoiceField(label=_('Ich trage mich ein:'))
    message = CharField(label=_('Mitteilung:'), widget=Textarea(attrs={"rows": 3}), required=False,
                        help_text=_('Diese Mitteilung wird an die Einsatz-Koordination gesendet'))

    text = {
        'options': {
            0: _('Abmelden'),
            1: _('Unbegleitet'),
            2: _('Zu Zweit'),
            3: _('Zu Dritt'),
            4: _('Zu Viert'),
            None: lambda x: _('{0} weitere Personen und ich').format(x - 1)
        },
    }
    message_wrapper_class = 'd-none'  # let js display the field if needed

    def __init__(self, member, job, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member = member
        self.job = job
        self.current_assignments = job.assignment_set.filter(member=member)
        self.current_slots = self.current_assignments.count()
        self.available_slots = self.MAX_VALUE if self.job.infinite_slots else self.job.free_slots + self.current_slots
        # form layout
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_id = 'job-subscribe-form'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-6'
        # create and configure fields
        if self.can_interact:
            self._set_up_form()
        else:
            del self.fields['slots']

    def _set_up_form(self):
        selected_extras = list(JobExtra.objects.filter(assignments__in=self.current_assignments))
        extras = []
        for extra in set(selected_extras + self.job.empty_per_job_extras() + list(self.job.per_member_extras())):
            field_name = f'extra{extra.extra_type.id}'
            self.fields[field_name] = BooleanField(label=extra.extra_type.name, required=False)
            extras.append(field_name)
        for selected_extra in selected_extras:
            self.initial[f'extra{selected_extra.extra_type.id}'] = True
        self.fields['slots'].choices = self.get_choices
        self.initial['slots'] = self.current_slots

        # show buttons depending on status
        allow_job_unsubscribe = Config.allow_job_unsubscribe()
        if self.current_slots > 0:
            actions = [Submit('subscribe', _('Ändern'), css_class='d-none',
                              data_message=_('Möchtest du deinen Einsatz verbindlich ändern?'))]
            if allow_job_unsubscribe:
                actions.append(Submit(self.UNSUBSCRIBE, _('Abmelden'), css_class='btn-danger d-none',
                                      data_message=_('Möchtest du dich wirklich abmelden?')))
        else:
            actions = [Submit('subscribe', _('Bestätigen'),
                              data_message=_('Möchtest du dich verbindlich für diesen Einsatz eintragen?'))]
        self.helper.layout = Layout(
            Field('slots', data_initial_slots=self.current_slots),
            *[Field(f, data_initial_checked=self.initial.get(f, False)) for f in extras],
            Field('message', wrapper_class=self.message_wrapper_class),
            FormActions(*actions),
        )
        if self.current_slots > 0:
            self.helper.layout.insert(-1, Div(
                HTML(get_template('messages/job_assigned.html').render(dict(others=self.current_slots - 1))),
                css_id='subscribed_info',
                css_class='offset-md-3 col-md-6 mb-3 d-none'
            ))
        if isinstance(allow_job_unsubscribe, str):
            # show info when unsubscribing or reducing
            self.helper.layout.insert(1, Div(
                HTML(allow_job_unsubscribe),
                css_id='unsubscribe_info',
                css_class='offset-md-3 col-md-6 mb-3 d-none'
            ))

    def get_option_text(self, index):
        return self.text['options'].get(index, self.text['options'][None](index))

    def get_choices(self):
        max_slots = min(self.available_slots, self.MAX_VALUE)
        min_slots = 0 if self.can_unsubscribe else max(1, self.current_slots)
        for i in range(min_slots, max_slots + 1):
            label = self.get_option_text(i)
            yield i, label

    @property
    def can_unsubscribe(self):
        return self.current_slots > 0 and Config.allow_job_unsubscribe()

    @property
    def can_interact(self):
        can_subscribe = self.available_slots > 0
        return self.job.start_time() > timezone.now() and not self.job.canceled and (can_subscribe or self.can_unsubscribe)

    def clean(self):
        if not self.can_interact:
            raise ValidationError(_("Du kannst an diesem Einsatz nichts ändern"), code='interaction_error')
        self.cleaned_data[self.UNSUBSCRIBE] = self.UNSUBSCRIBE in self.data
        if (self.cleaned_data[self.UNSUBSCRIBE] or self.cleaned_data.get('slots') == '0') and not self.can_unsubscribe:
            raise ValidationError(_("Du kannst dich nicht aus dem Einsatz austragen"), code='unsubscribe_error')
        return super().clean()

    def save(self):
        slots = int(self.cleaned_data['slots'])

        # handle unsubscribe action
        if self.cleaned_data[self.UNSUBSCRIBE] or slots == 0:
            self.current_assignments.delete()

        # handle subscribe action
        else:
            with transaction.atomic():
                # clear current slots of member and fill new
                self.current_assignments.delete()
                assignment = Assignment(
                    member=self.member,
                    job=self.job,
                    amount=self.get_multiplier(),
                    core_cache=self.job.type.activityarea.core
                )
                Assignment.objects.bulk_create([assignment] * slots)

                # apply job extras
                assignment = Assignment.objects.filter(member=self.member, job=self.job).last()
                for extra in self.job.type.job_extras_set.all():
                    if self.cleaned_data['extra' + str(extra.extra_type.id)]:
                        assignment.job_extras.add(extra)
                assignment.save()
        self.send_signals(slots, self.cleaned_data['message'])

    def get_multiplier(self):
        unit = Config.assignment_unit()
        if unit == 'ENTITY':
            return self.job.multiplier
        elif unit == 'HOURS':
            return self.job.multiplier * self.job.duration
        return 1

    def send_signals(self, slots, message=''):
        # send signals
        subscribed.send(Job, instance=self.job, member=self.member, count=slots, initial_count=self.current_slots,
                        message=message)


class EditAssignmentForm(JobSubscribeForm):
    message_wrapper_class = None  # always show message field

    text = dict(
        message_to_member=gettext_lazy('Mitteilung an das Mitglied'),
        slots_label=gettext_lazy('Teilnahme'),
        option_1=gettext_lazy('Alleine'),
        option_x=gettext_lazy('{0} Personen'),
        **JobSubscribeForm.text,
    )

    def __init__(self, editor, can_delete, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editor = editor
        self.can_delete = can_delete
        self.helper.form_id = 'assignment-edit-form'
        self.fields['message'].help_text = self.text['message_to_member']
        self.fields['slots'].label = self.text['slots_label']

    def get_option_text(self, index):
        if index == 1:
            return self.text['option_1']
        return self.text['options'].get(index, self.text['option_x'].format(index))

    @property
    def can_unsubscribe(self):
        return self.can_delete

    @property
    def can_interact(self):
        return True

    def send_signals(self, slots, message=''):
        assignment_changed.send(
            Member, instance=self.member, job=self.job, editor=self.editor,
            count=slots, initial_count=self.current_slots,
            message=message
        )


class ConvertToRecurringJobForm(Form):
    job_type = ModelChoiceField(
        JobType.objects.filter(visible=True),  # TODO: limit selection to coordinated areas
        required=False,
        label=_('Umwandlung der Job-Art'),
        help_text=_('Falls eine bestehende Job-Art gewählt wird, werden einige Daten vom Einzeljob überschrieben.'
                    'Ohne Auswahl wird eine neue Job-Art aus den Angaben des Einzeljobs erstellt'),
        empty_label=_('Neue Job-Art erstellen'),
        widget=ModelSelect2Widget(
            model=JobType,
            search_fields=[
                'name__icontains', 'displayed_name__icontains', 'activityarea__name__icontains'
            ],
            data_view='internal-select2-view'
        )
    )

    def save(self, one_time_job):
        return one_time_job.convert(self.cleaned_data['job_type'])
