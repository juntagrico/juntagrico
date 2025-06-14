import html
import re

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Fieldset, HTML
from django import forms
from django.core.mail import EmailMultiAlternatives
from django.forms import Media
from django.template.loader import get_template
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget
from djrichtextfield.widgets import RichTextWidget

from juntagrico.config import Config
from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import ActivityArea, Job
from juntagrico.entity.mailing import MailTemplate
from juntagrico.entity.member import Member


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
        return f'{obj.type.get_name} ({date_format(obj.time, "SHORT_DATETIME_FORMAT")})'


class EmailRecipientsForm(forms.Form):
    to_list = forms.MultipleChoiceField(label=False, required=False, widget=forms.CheckboxSelectMultiple)
    to_areas = forms.ModelMultipleChoiceField(
        ActivityArea.objects.none(), label=_('An alle in diesen Tätigkeitsbereichen'), required=False,
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
        label=_('An alle mit aktivem/r {} in diesen Depots').format(Config.vocabulary('subscription')),
        required=False,
        widget=InternalModelSelect2MultipleWidget(
            model=Depot,
            search_fields=['name__icontains', 'id__icontains'],
            attrs={'data-minimum-input-length': 0}
        )
    )
    to_members = forms.ModelMultipleChoiceField(
        Member.objects.active(), label=_('An diese Personen'), required=False, widget=InternalModelSelect2MultipleWidget(
            model=Member,
            search_fields=[
                'first_name__icontains',
                'last_name__icontains',
                'email__icontains',
            ],
        )
    )
    # TODO: the copy to self would ideally list the recipients
    #  and contain a link to open the form again with the same recipients.
    copy = forms.BooleanField(label=_('Kopie an mich'), required=False)

    def __init__(self, sender, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sender = sender
        self.fields['to_list'].choices = self.get_recipient_list_choices()
        # TODO: limit selection of areas, depots and members
        self.fields['to_areas'].queryset = ActivityArea.objects.all()

    def get_form_layout(self):
        return Fieldset(
            _('An'),
            'to_list', 'to_areas', 'to_jobs', 'to_depots', 'to_members', 'copy',
            css_id='fieldset_to', css_class='my-5'
        )

    def get_recipient_list_choices(self):
        # TODO: only show options based on members permissions (future)
        return [
            ('all', _('Alle')),  # TODO: Challenge the existence of this option
            ('all_subscriptions', _('Alle mit aktivem/r {}').format(Config.vocabulary('subscription')),),
            ('all_shares', _('Alle mit {}').format(Config.vocabulary('share')),),
        ]

    def _get_recipients_queryset(self):
        cleaned_data = self.cleaned_data
        if 'all' in cleaned_data['to_list']:
            # return all members directly
            return Member.objects.active()

        recipients = Member.objects.none()
        if 'all_subscriptions' in cleaned_data['to_list']:
            recipients |= Member.objects.active().has_active_subscription()
        elif cleaned_data['to_depots']:
            recipients |= Member.objects.active().has_active_subscription().in_depot(cleaned_data['to_depots'])
        if 'all_shares' in cleaned_data['to_list']:
            recipients |= Member.objects.active().has_active_shares()
        if cleaned_data['to_areas']:
            recipients |= Member.objects.active().filter(areas__in=cleaned_data['to_areas'])
        if cleaned_data['to_jobs']:
            recipients |= Member.objects.active().filter(assignment__job__in=cleaned_data['to_jobs'])
        if cleaned_data['to_members']:
            recipients |= Member.objects.active().filter(pk__in=cleaned_data['to_members'])
        if cleaned_data['copy']:
            recipients |= Member.objects.active().filter(pk__in=[self.sender.pk])
        return recipients.distinct()

    def _get_recipients(self):
        return set(self._get_recipients_queryset().as_email_recipients())

    def count_recipients(self):
        return self._get_recipients_queryset().count()


class EmailForm(EmailRecipientsForm):
    from_email = forms.ChoiceField(label=_('Von'))
    subject = forms.CharField(label=_('Betreff'))
    body = forms.CharField(label=_('Nachricht'), required=False, widget=RichTextWidget(field_settings='juntagrico.mailer'))

    def __init__(self, sender, features, *args, **kwargs):
        super().__init__(sender, *args, **kwargs)
        self.fields['from_email'].choices = self.get_sender_choices()
        if features['template']:
            self.fields['body'].widget = RichTextWidgetWithTemplates(field_settings='juntagrico.mailer')
        if features['attachment']:
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
            'from_email',
            super().get_form_layout(),
            'subject', 'body',
            HTML(get_template('juntagrico/email/snippets/signature_display.html').render()),
            FormActions(
                Submit(
                    'submit', _('Senden'), css_class='btn-success btn-lg',
                    data_count_url=reverse('email-count-recipients')
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
        text = raw_html.replace('\n', '\n\n')
        text = re.sub('<br ?/?>', '\n', text, flags=re.IGNORECASE)
        text = html.unescape(text)
        return strip_tags(text)

    def send(self):
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']

        html_body = get_template('mails/email.html').render({
            'subject': subject, 'content': body
        })
        text_body = get_template('mails/email.txt').render({
            'subject': subject, 'content': self._html_to_text(body)
        })

        email = EmailMultiAlternatives(
            self.cleaned_data['subject'],
            text_body,
            dict(self.fields['from_email'].choices)[self.cleaned_data['from_email']],
            # TODO: if there is only one recipient (besides copy to self) use to field directly.
            bcc=self._get_recipients(),
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
