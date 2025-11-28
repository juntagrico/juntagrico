import html

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Fieldset, HTML
from django import forms
from django.core.mail import EmailMultiAlternatives
from django.db.models import OuterRef, Exists
from django.forms import Media
from django.template.loader import get_template
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget
from djrichtextfield.widgets import RichTextWidget

from juntagrico.config import Config
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea, Job
from juntagrico.entity.mailing import MailTemplate
from juntagrico.entity.member import Member
from juntagrico.util.html import EmailHtmlParser


class RichTextWidgetWithTemplates(RichTextWidget):
    def render(self, name, value, attrs=None, renderer=None):
        template_html = get_template('juntagrico/email/snippets/template_selection.html').render({
            'templates': MailTemplate.objects.all()
        })
        return super().render(name, value, attrs, renderer) + template_html

    @property
    def media(self):
        return super().media + Media(js=['juntagrico/js/forms/templateLoader.js'])


class MultipleFileInput(forms.FileInput):
    @property
    def media(self):
        return super().media + Media(js=['juntagrico/js/forms/attachmentAppender.js'])


class InternalModelSelect2MultipleWidget(ModelSelect2MultipleWidget):
    def __init__(self, *args, **kwargs):
        kwargs['data_view'] = 'internal-select2-view'
        super().__init__(*args, **kwargs)


class JobSelect2MultipleWidget(InternalModelSelect2MultipleWidget):
    def label_from_instance(self, obj):
        return obj.get_label()


class MemberSelect2MultipleWidget(InternalModelSelect2MultipleWidget):
    model = Member
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
        'email__icontains',
    ]

    def get_queryset(self):
        # annotate if another member with the exact same name exists
        return super().get_queryset().annotate(
            duplicate=Exists(
                Member.objects.exclude(pk=OuterRef('pk')).filter(
                    first_name=OuterRef('first_name'),
                    last_name=OuterRef('last_name')
                )
            )
        )

    def label_from_instance(self, obj):
        label = super().label_from_instance(obj)
        if getattr(obj, 'duplicate', False):
            label += f' ({date_format(obj.user.date_joined, "SHORT_DATE_FORMAT")})'
        return label


class BaseRecipientsForm(forms.Form):
    to_members = forms.ModelMultipleChoiceField(
        Member.objects.active(), label=_('An diese Personen'), required=False, widget=MemberSelect2MultipleWidget
    )
    # TODO: the copy to self would ideally list the recipients
    #  and contain a link to open the form again with the same recipients.
    copy = forms.BooleanField(label=_('Kopie an mich'), required=False)

    form_fields = ['to_members', 'copy']

    def __init__(self, sender, *args, areas=None, depots=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sender = sender
        if 'to_members' in self.fields:
            if areas is not None or depots is not None:
                members = Member.objects.filter(reachable_by_email=True)
                if depots is not None:
                    members |= Member.objects.has_active_subscription().in_depot(depots)
                if areas is not None:
                    members |= Member.objects.filter(areas__in=areas)
                    members |= Member.objects.filter(assignment__job__in=Job.objects.in_areas(areas))
                self.fields['to_members'].queryset = members.active().distinct()

    def get_form_layout(self):
        return Fieldset(
            _('An'),
            *self.form_fields,
            css_id='fieldset_to', css_class='my-5'
        )

    def _populate_recipients_queryset(self, recipients):
        cleaned_data = self.cleaned_data
        if to_members := cleaned_data.get('to_members'):
            recipients |= Member.objects.active().filter(pk__in=to_members)
        if cleaned_data.get('copy'):
            recipients |= Member.objects.active().filter(pk__in=[self.sender.pk])
        return recipients

    def _get_recipients_queryset(self):
        recipients = Member.objects.none()
        recipients = self._populate_recipients_queryset(recipients)
        return recipients.distinct()

    def _get_recipients(self):
        return set(self._get_recipients_queryset().as_email_recipients())

    def get_count_url(self):
        return reverse('email-count-recipients')

    def count_recipients(self):
        return self._get_recipients_queryset().count()


class RecipientsForm(BaseRecipientsForm):
    to_list = forms.MultipleChoiceField(label=False, required=False, widget=forms.CheckboxSelectMultiple)
    to_areas = forms.ModelMultipleChoiceField(
        ActivityArea.objects.order_by('name'), label=_('An alle in diesen Tätigkeitsbereichen'), required=False,
        widget=InternalModelSelect2MultipleWidget(
            model=ActivityArea,
            search_fields=['name__icontains'],
            attrs={'data-minimum-input-length': 0}
        )
    )
    to_jobs = forms.ModelMultipleChoiceField(
        Job.objects.order_by_recent(), label=_('An alle in diesen Einsätzen'), required=False,
        widget=JobSelect2MultipleWidget(
            model=Job,
            search_fields=[
                'OneTimeJob___name__icontains', 'OneTimeJob___displayed_name__icontains',
                'RecuringJob___type__name__icontains', 'RecuringJob___type__displayed_name__icontains',
                'time__icontains'
            ],
            attrs={'data-minimum-input-length': 4}
        )
    )
    to_depots = forms.ModelMultipleChoiceField(
        Depot.objects.order_by('id'),
        label=_('An alle mit aktivem/r {} in diesen {}').format(Config.vocabulary('subscription'), Config.vocabulary('depot_pl')),
        required=False,
        widget=InternalModelSelect2MultipleWidget(
            model=Depot,
            search_fields=['name__icontains', 'id__icontains'],
            attrs={'data-minimum-input-length': 0}
        )
    )

    form_fields = ['to_list', 'to_areas', 'to_jobs', 'to_depots', 'to_members', 'copy']

    def __init__(self, sender, *args, areas=None, depots=None, **kwargs):
        super().__init__(sender, *args, areas=areas, depots=depots, **kwargs)
        # configure fields
        if 'to_list' in self.fields:
            if choices := self.get_recipient_list_choices():
                self.fields['to_list'].choices = choices
            else:
                del self.fields['to_list']
                self.form_fields.remove('to_list')
        # limit selectable values
        if 'to_areas' in self.fields:
            self._set_field_queryset('to_areas', (areas or ActivityArea.objects.all()).order_by('name'))
        if 'to_jobs' in self.fields:
            if areas is not None:
                self._set_field_queryset('to_jobs', Job.objects.in_areas(areas))
        if 'to_depots' in self.fields:
            self._set_field_queryset(
                'to_depots',
                (depots or Depot.objects).order_by('id')
            )

    def _set_field_queryset(self, field, queryset):
        if not queryset.exists():
            del self.fields[field]
            self.form_fields.remove(field)
        else:
            self.fields[field].queryset = queryset

    def get_recipient_list_choices(self):
        choices = []
        if self.sender.user.has_perm('juntagrico.can_email_all_with_sub'):
            choices.append((
                'all_subscriptions',
                _('Alle mit aktivem/r {}').format(Config.vocabulary('subscription'))
            ))
        if Config.enable_shares() and self.sender.user.has_perm('juntagrico.can_email_all_with_share'):
            choices.append((
                'all_shares',
                _('Alle mit {}').format(Config.vocabulary('share'))
            ))
        return choices

    def _populate_recipients_queryset(self, recipients):
        cleaned_data = self.cleaned_data
        to_list = cleaned_data.get('to_list', [])
        if 'all_subscriptions' in to_list:
            recipients |= Member.objects.active().has_active_subscription()
        elif to_depots := cleaned_data.get('to_depots'):
            recipients |= Member.objects.active().has_active_subscription().in_depot(to_depots)
        if 'all_shares' in to_list:
            recipients |= Member.objects.active().has_active_shares()
        if to_areas := cleaned_data.get('to_areas'):
            recipients |= Member.objects.active().filter(areas__in=to_areas)
        if to_jobs := cleaned_data.get('to_jobs'):
            recipients |= Member.objects.active().filter(assignment__job__in=to_jobs)
        return super()._populate_recipients_queryset(recipients)

    def _get_recipients_queryset(self):
        if 'all' in self.cleaned_data.get('to_list', []):
            # return all members directly
            return Member.objects.active()

        recipients = Member.objects.none()
        recipients = self._populate_recipients_queryset(recipients)
        return recipients.distinct()


class DepotRecipientsForm(BaseRecipientsForm):
    to_depot = forms.BooleanField(
        label=_('An alle mit aktivem/r {} in {} {}').format(Config.vocabulary('subscription'), Config.vocabulary('depot'), '{}'),
        required=False
    )

    form_fields = ['to_depot', *BaseRecipientsForm.form_fields]

    def __init__(self, sender, depot_id, *args, **kwargs):
        super().__init__(sender, *args, **kwargs)
        self.depot_id = depot_id
        depot = Depot.objects.get(pk=self.depot_id)
        self.fields['to_depot'].label = self.fields['to_depot'].label.format(depot.name)
        self.fields['to_members'].label = _('An diese Personen in {}').format(Config.vocabulary('depot'))
        self.fields['to_members'].queryset = Member.objects.active().has_active_subscription().in_depot(self.depot_id)

    def get_count_url(self):
        return reverse('email-count-depot-recipients', args=[self.depot_id])

    def _populate_recipients_queryset(self, recipients):
        if self.cleaned_data.get('to_depot'):
            recipients |= Member.objects.active().has_active_subscription().in_depot(self.depot_id)
        return super()._populate_recipients_queryset(recipients)


class AreaRecipientsForm(BaseRecipientsForm):
    to_area = forms.BooleanField(
        label=_('An alle Personen im Tätigkeitsbereich {}'),
        required=False
    )

    form_fields = ['to_area', *BaseRecipientsForm.form_fields]

    def __init__(self, sender, area_id, *args, **kwargs):
        super().__init__(sender, *args, **kwargs)
        self.area_id = area_id
        area = ActivityArea.objects.get(pk=self.area_id)
        self.fields['to_area'].label = self.fields['to_area'].label.format(area.name)
        self.fields['to_members'].label = _('An diese Personen im Tätigkeitsbereich')
        self.fields['to_members'].queryset = area.members.active()

    def get_count_url(self):
        return reverse('email-count-area-recipients', args=[self.area_id])

    def _populate_recipients_queryset(self, recipients):
        if self.cleaned_data.get('to_area'):
            recipients |= ActivityArea.objects.get(pk=self.area_id).members.active()
        return super()._populate_recipients_queryset(recipients)


class JobRecipientsForm(BaseRecipientsForm):
    to_job = forms.BooleanField(
        label=_('An alle Personen im Einsatz "{}"'),
        required=False
    )

    form_fields = ['to_job', *BaseRecipientsForm.form_fields]

    def __init__(self, sender, job_id, *args, **kwargs):
        super().__init__(sender, *args, **kwargs)
        self.job_id = job_id
        job = Job.objects.get(pk=self.job_id)
        self.fields['to_job'].label = self.fields['to_job'].label.format(job.get_label())
        self.fields['to_members'].label = _('An diese Personen im Einsatz')
        self.fields['to_members'].widget.attrs['data-minimum-input-length'] = 0
        self.fields['to_members'].queryset = job.members.active()

    def get_count_url(self):
        return reverse('email-count-job-recipients', args=[self.job_id])

    def _populate_recipients_queryset(self, recipients):
        if self.cleaned_data.get('to_job'):
            recipients |= Job.objects.get(pk=self.job_id).members.active()
        return super()._populate_recipients_queryset(recipients)


class BaseForm(BaseRecipientsForm):
    from_email = forms.ChoiceField(label=_('Von'))
    subject = forms.CharField(label=_('Betreff'))
    body = forms.CharField(label=_('Nachricht'), required=False, widget=RichTextWidget(field_settings='juntagrico.mailer'))

    def __init__(self, sender, *args, templates=False, attachments=False, **kwargs):
        super().__init__(sender, *args, **kwargs)
        self.sender = sender
        self.fields['from_email'].choices = self.get_sender_choices()
        if templates:
            self.fields['body'].widget = RichTextWidgetWithTemplates(field_settings='juntagrico.mailer')
        if attachments:
            self.fields['attachments0'] = forms.FileField(label=_('Anhänge'), required=False, widget=MultipleFileInput)
            # collect attachments
            for attachments in self.files.keys():
                if attachments != 'attachments0':
                    self.fields[attachments] = forms.FileField(required=False)
        # form layout
        self.helper = FormHelper()
        self.helper.layout = self.get_form_layout()

    def get_form_layout(self):
        layout = Layout(
            Field('from_email', css_class='custom-select-lg'),
            super().get_form_layout(),
            Field('subject', css_class='form-control-lg'), 'body',
            HTML(get_template('juntagrico/email/snippets/signature_display.html').render({
                'footer': self.get_footer()
            })),
            FormActions(
                Submit(
                    'submit', _('Senden'), css_class='btn-success btn-lg',
                    data_count_url=self.get_count_url()
                ),
                css_class='text-right'
            ),
        )
        if 'attachments0' in self.fields:
            layout.insert(-3, Field('attachments0', template='juntagrico/email/widgets/file.html'))
        return layout

    def get_sender_choices(self):
        base = Config.vocabulary('from').format(self.sender.first_name, Config.organisation_name()) + ' <{}>'
        return [(identifier, base.format(email)) for identifier, email in self.sender.all_emails()]

    def _html_to_text(self, raw_html):
        parser = EmailHtmlParser()
        parser.feed(raw_html)
        return html.unescape(parser.text)

    def get_footer(self):
        """ Override to add a footer to the email
        :return: html email footer
        """
        return ''

    def send(self):
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        footer = self.get_footer()

        html_body = get_template('mails/email.html').render({
            'subject': subject, 'content': mark_safe(body), 'footer': footer
        })
        text_body = get_template('mails/email.txt').render({
            'subject': subject, 'content': self._html_to_text(body), 'footer': self._html_to_text(footer.strip())
        })

        email = EmailMultiAlternatives(
            self.cleaned_data['subject'],
            text_body,
            dict(self.fields['from_email'].choices)[self.cleaned_data['from_email']],
            # TODO: if there is only one recipient (besides copy to self) use to field directly.
            bcc=list(self._get_recipients()),
            alternatives=[(html_body, 'text/html')],
        )
        # add attachments
        attachment_num = 0
        while attachment := self.cleaned_data.get(f'attachments{attachment_num}'):
            email.attach(attachment.name, attachment.read())
            attachment_num += 1
        # send email(s)
        return email.send()

    class Media:
        js = ['juntagrico/js/forms/emailForm.js']


class EmailForm(BaseForm, RecipientsForm):
    pass


class MemberForm(BaseForm):
    pass


class DepotForm(BaseForm, DepotRecipientsForm):
    def get_footer(self):
        return get_template('juntagrico/mails/footer/depot.html').render({
            'depot': Depot.objects.get(pk=self.depot_id)
        })


class AreaForm(BaseForm, AreaRecipientsForm):
    def get_footer(self):
        return get_template('juntagrico/mails/footer/area.html').render({
            'area': ActivityArea.objects.get(pk=self.area_id)
        })


class JobForm(BaseForm, JobRecipientsForm):
    def get_footer(self):
        return get_template('juntagrico/mails/footer/job.html').render({
            'job': Job.objects.get(pk=self.job_id)
        })
