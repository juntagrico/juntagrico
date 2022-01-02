from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, HTML, Div
from django.forms import CharField, PasswordInput, Form, ValidationError, \
    ModelForm, DateInput, IntegerField, BooleanField, HiddenInput, Textarea
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from schwifty import IBAN

from juntagrico.config import Config
from juntagrico.dao.memberdao import MemberDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao
from juntagrico.models import Member, Subscription


class Slider(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(template='forms/slider.html', css_class='slider', *args, **kwargs)


class LinkButton(HTML):
    def __init__(self, name, href, css_classes=None):
        super().__init__(f'<a href="{href}" class="btn {css_classes}">{name}</a>')


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

    @staticmethod
    def duplicate_email_message():
        return mark_safe(
            escape(_('Diese E-Mail-Adresse existiert bereits im System.')) + '<a href="' + reverse(
                "home") + '">' + escape(_('Hier geht\'s zum Login.')) + '</a>'
        )

    def clean_email(self):
        # check case insensitive uniqueness, because existing emails might already be upper case
        if Member.objects.filter(email__iexact=self.cleaned_data['email']):
            raise ValidationError(self.duplicate_email_message())
        # store email in lower case from now on
        return self.cleaned_data['email'].lower()


class RegisterMemberForm(MemberBaseForm):
    comment = CharField(required=False, max_length=4000, label='Kommentar', widget=Textarea(attrs={"rows": 3}))
    agb = BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agb'].label = self.agb_label()
        self.helper.layout = Layout(
            *self.base_layout,
            'comment',
            'agb',
            FormActions(
                Submit('submit', _('Anmelden'), css_class='btn-success'),
            )
        )
        self.fields['email'].error_messages['unique'] = self.duplicate_email_message()

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


class RegisterSummaryForm(Form):
    comment = CharField(required=False, max_length=4000, label='',
                        widget=Textarea(attrs={"rows": 3, "class": "textarea form-control"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'comment',
            FormActions(
                Submit('submit', _('Verbindlich bestellen'), css_class='btn btn-success'),
                HTML('<a href="{0}" class="btn">{1}</a>'.format(reverse('cs-cancel'), _("Abbrechen")))
            )
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
        email = self.cleaned_data['email'].lower()
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
        # disable default uniqueness check
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
                LinkButton(_("Abbrechen"), reverse("sub-detail")),
            )
        )


class RegisterMultiCoMemberForm(CoMemberBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            *self.base_layout,  # keep first 9 fields
            FormActions(
                self.get_submit_button(),
                LinkButton(self.button_next_text(), '?next', css_classes='btn-success'),
                LinkButton(_('Abbrechen'), reverse("cs-cancel"))
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
                LinkButton(_('Abbrechen'), '?')
            )
        )


class CategoryContainer(Div):
    template = "forms/layout/category_container.html"

    def __init__(self, *fields, instance, name=None, description=None, **kwargs):
        super().__init__(*fields, **kwargs)
        self.instance = instance
        self.name = name or instance.name
        self.description = description or instance.description


class SubscriptionTypeField(Field):
    template = 'forms/subscription_type_field.html'

    def __init__(self, *args, instance, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    def render(self, *args, **kwargs):
        extra_context = kwargs.pop('extra_context', {})
        extra_context['type'] = self.instance
        return super().render(*args, extra_context=extra_context, **kwargs)


class SubscriptionPartBaseForm(Form):
    def __init__(self, *args, product_method=SubscriptionProductDao.get_visible_normal_products, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self._product_method = product_method

    def _collect_type_fields(self):
        containers = []
        for product in self._product_method().all():
            product_container = CategoryContainer(instance=product)
            for subscription_size in product.sizes.filter(visible=True):
                size_container = CategoryContainer(instance=subscription_size, name=subscription_size.long_name)
                for subscription_type in subscription_size.types.filter(visible=True):
                    field_name = f'amount[{subscription_type.id}]'
                    self.fields[field_name] = IntegerField(label=subscription_type.name, min_value=0,
                                                           initial=self._get_initial(subscription_type))

                    size_container.append(SubscriptionTypeField(field_name, instance=subscription_type))
                product_container.append(size_container)
            containers.append(product_container)
        return containers

    def _get_initial(self, subscription_type):
        raise NotImplementedError

    def get_selected(self):
        return {
            sub_type: getattr(self, 'cleaned_data', {}).get('amount[' + str(sub_type.id) + ']', 0)
            for sub_type in SubscriptionTypeDao.get_all()
        }


class SubscriptionPartSelectForm(SubscriptionPartBaseForm):
    def __init__(self, selected, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected = selected
        containers = self._collect_type_fields()

        self.fields['no_subscription'] = BooleanField(label=_('Kein {}').format(Config.vocabulary('subscription')),
                                                      initial=True, required=False)

        self.helper.layout = Layout(
            *containers,
            Field('no_subscription', template='forms/no_subscription_field.html'),
            FormActions(
                Submit('submit', _('Weiter'), css_class='btn-success'),
                LinkButton(_('Abbrechen'), reverse('cs-cancel'))
            )
        )

    def _get_initial(self, subscription_type):
        if subscription_type in self.selected.keys():
            return self.selected[subscription_type]
        return 0


class SubscriptionPartOrderForm(SubscriptionPartBaseForm):
    def __init__(self, subscription=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscription = subscription
        self.helper.layout = Layout(
            *self._collect_type_fields(),
            FormActions(
                Submit('submit', _('{}-Bestandteile bestellen').format(Config.vocabulary('subscription')),
                       css_class='btn-success')
            )
        )

    def _get_initial(self, subscription_type):
        return 0

    def clean(self):
        selected = self.get_selected()
        # check if members in subscription have sufficient shares
        available_shares = self.subscription.all_shares
        new_required_shares = sum([sub_type.shares * amount for sub_type, amount in selected.items()])
        existing_required_shares = self.subscription.required_shares
        if available_shares < new_required_shares + existing_required_shares:
            share_error_message = mark_safe(_('Es sind zu wenig {} vorhanden für diese Bestandteile!{}').format(
                Config.vocabulary('share_pl'),
                '<br/><a href="{}" class="alert-link">{}</a>'.format(
                    reverse('manage-shares'), _('&rarr; Bestelle hier mehr {}').format(Config.vocabulary('share_pl')))
            ))
            raise ValidationError(share_error_message, code='share_error')
        # check that at least one subscription was selected
        if sum(selected.values()) == 0:
            amount_error_message = mark_safe(_('Wähle mindestens 1 {} aus.{}').format(
                Config.vocabulary('subscription'),
                '<br/><a href="{}" class="alert-link">{}</a>'.format(
                    reverse('sub-cancel', args=[self.subscription.id]),
                    _('&rarr; Oder {} komplett künden').format(Config.vocabulary('subscription')))
            ))
            raise ValidationError(amount_error_message, code='amount_error')
        return super().clean()


class NicknameForm(Form):
    nickname = CharField(label=_('{}-Spitzname').format(Config.vocabulary('subscription')), max_length=30, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Speichern')))
