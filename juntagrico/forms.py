from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, HTML
from django.forms import CharField, PasswordInput, Form, ValidationError, \
    ModelForm, DateInput, IntegerField, BooleanField, HiddenInput
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from schwifty import IBAN

from juntagrico.config import Config
from juntagrico.dao.memberdao import MemberDao
from juntagrico.models import Member, Subscription


class Slider(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(template='forms/slider.html', css_class='slider', *args, **kwargs)


class PasswordForm(Form):
    password = CharField(label=_('Passwort'), min_length=4,
                         widget=PasswordInput())
    passwordRepeat = CharField(
        label=_('Passwort (wiederholen)'), min_length=4, widget=PasswordInput())

    def clean_password_repeat(self):
        if self.data['password'] != self.data['passwordRepeat']:
            raise ValidationError(_('Passwörter stimmen nicht überein'))
        return self.data['passwordRepeat']


class MemberProfileForm(ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email',
                  'addr_street', 'addr_zipcode', 'addr_location',
                  'birthday', 'phone', 'mobile_phone', 'iban', 'reachable_by_email']
        labels = {
            "phone": _("Telefonnummer"),
            "email": _("E-Mail-Adresse"),
            "birthday": _("Geburtstag"),
            "addr_street": _("Strasse/Nr."),
            "reachable_by_email": _(
                'Sollen andere {} dich via Kontaktformular erreichen können? (Email nicht sichtbar)'
            ).format(Config.vocabulary('member_pl')),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].disabled = True
        self.fields['last_name'].disabled = True
        self.fields['email'].disabled = True
        self.fields['last_name'].help_text = self.contact_admin_link(_('Kontaktiere {} um den Namen zu ändern.'))
        self.fields['email'].help_text = self.contact_admin_link(_('Kontaktiere {} um die E-Mail-Adresse zu ändern.'))

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'

        self.helper.layout = Layout(
            'first_name', 'last_name',
            'addr_street', 'addr_zipcode', 'addr_location',
            'phone', 'mobile_phone', 'email', 'birthday', 'iban',
            Slider('reachable_by_email'),
            FormActions(
                Submit('submit', _('Personalien ändern'), css_class='btn-success'),
            ),
        )

    @staticmethod
    def contact_admin_link(text):
        return mark_safe(
            escape(
                text
            ).format('<a href="mailto:{0}">{0}</a>'.format(Config.info_email()))
        )

    def clean_iban(self):
        if self.data['iban'] != '':
            try:
                IBAN(self.data['iban'])
            except ValueError:
                raise ValidationError(_('IBAN ist nicht gültig'))
        return self.data['iban']


class SubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ['start_date']
        widgets = {
            'start_date': DateInput(attrs={'format': '%d.%m.%y', 'class': 'form-control'}),
        }


class MemberBaseForm(ModelForm):
    class Meta:
        model = Member
        fields = ('first_name', 'last_name', 'email',
                  'addr_street', 'addr_zipcode', 'addr_location',
                  'birthday', 'phone', 'mobile_phone')
        labels = {
            "phone": _("Telefonnummer"),
            "email": _("E-Mail-Adresse"),
            "birthday": _("Geburtstag"),
            "addr_street": _("Strasse/Nr."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.existing_member = None
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.base_layout = ('last_name', 'first_name',
                            'addr_street', 'addr_zipcode', 'addr_location',
                            'phone', 'mobile_phone', 'email', 'birthday')


class RegisterMemberForm(MemberBaseForm):
    agb = BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agb'].label = self.agb_label()
        self.helper.layout = Layout(
            *self.base_layout,
            'agb',
            FormActions(
                Submit('submit', _('Anmelden'), css_class='btn-success'),
            )
        )
        self.fields['email'].error_messages['unique'] = mark_safe(
            escape(_('Diese E-Mail-Adresse existiert bereits im System.')) + '<a href="' + reverse("home") + '">' + escape(_('Hier geht\'s zum Login.')) + '</a>'
        )

    @staticmethod
    def agb_label():
        return _('Ich habe {}{}{} gelesen und erkläre meinen Willen, "{}" beizutreten.\
            Hiermit beantrage ich meine Aufnahme.').format(
            '<a target="_blank" href="{}">{}</a>'.format(Config.bylaws(), _('die Statuten')),
            ' ' + _('und') + ' <a target="_blank" href="{}">{}</a>'.format(
                Config.business_regulations(), _('das Betriebsreglement')
            ) if Config.business_regulations().strip() else '',
            ' ' + _('und') + ' <a target="_blank" href="{}">{}</a>'.format(
                Config.gdpr_info(), _('die DSGVO Infos')
            ) if Config.gdpr_info().strip() else '',
            Config.organisation_long_name()
        )


class EditMemberForm(RegisterMemberForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['agb'] = True
        self.helper.layout = Layout(
            *self.helper.layout[:-1],
            FormActions(
                Submit('submit', _('Ändern'), css_class='btn-success'),
            )
        )


class CoMemberBaseForm(MemberBaseForm):
    def __init__(self, *args, existing_emails=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.existing_emails = existing_emails or []  # list of emails that can not be used

    def clean_email(self):
        email = self.cleaned_data['email']
        if email in self.existing_emails:
            raise ValidationError(mark_safe(_('Diese E-Mail-Adresse wird bereits von dir oder deinen {} verwendet.')
                                            .format(Config.vocabulary('co_member_pl'))))
        existing_member = MemberDao.member_by_email(email)
        if existing_member:
            if existing_member.blocked:
                raise ValidationError(mark_safe(escape(_('Die Person mit dieser E-Mail-Adresse ist bereits aktiv\
                 {}-BezierIn. Bitte meldet euch bei {}, wenn ihr bestehende {} als {} hinzufügen möchtet.')).format(
                    Config.vocabulary('subscription'),
                    '<a href="mailto:{0}">{0}</a>'.format(Config.info_email()),
                    Config.vocabulary('member_type_pl'),
                    Config.vocabulary('co_member_pl')
                )))
            else:
                # store existing member for reevaluation
                self.existing_member = existing_member
        return email

    def clean(self):
        return self.cleaned_data

    @staticmethod
    def get_submit_button():
        return Submit('submit', _('{} hinzufügen').format(Config.vocabulary('co_member')), css_class='btn-success')


class AddCoMemberForm(CoMemberBaseForm):
    shares = IntegerField(label=Config.vocabulary('share_pl'), required=False, min_value=0, initial=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = list(self.base_layout)  # keep first 9 fields
        if Config.enable_shares():
            fields.append(Field('shares', css_class='col-md-2'))
        self.helper.layout = Layout(
            *fields,
            FormActions(
                self.get_submit_button(),
                HTML('<a href="' + reverse("sub-detail") + '" class="btn">' + _("Abbrechen") + '</a>'),
            )
        )


class RegisterMultiCoMemberForm(CoMemberBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            *self.base_layout,  # keep first 9 fields
            FormActions(
                self.get_submit_button(),
                HTML('<a href="?next" class="btn btn-success">' + self.button_next_text() + '</a>'),
                HTML('<a href="' + reverse("cs-cancel") + '" class="btn">' + _('Abbrechen') + '</a>')
            )
        )

    def button_next_text(self):
        return _('Keine weiteren {} hinzufügen').format(Config.vocabulary('co_member_pl'))


class RegisterFirstMultiCoMemberForm(RegisterMultiCoMemberForm):
    def button_next_text(self):
        return _('Überspringen')


class EditCoMemberForm(CoMemberBaseForm):
    edit = IntegerField(widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # do not edit existing co-members
        if self.instance.pk:
            for field in self.fields.values():
                field.disabled = True

        self.helper.layout = Layout(
            *self.base_layout,  # keep first 9 fields
            'edit',
            FormActions(
                Submit('submit', _('Ändern'), css_class='btn-success'),
                HTML('<a href="?" class="btn">' + _('Abbrechen') + '</a>')
            )
        )
