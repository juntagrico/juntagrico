import datetime

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, HTML, Div, Fieldset
from crispy_forms.utils import TEMPLATE_PACK
from django.forms import CharField, PasswordInput, Form, ValidationError, \
    ModelForm, DateInput, IntegerField, BooleanField, HiddenInput, Textarea, ChoiceField, DateField, FloatField, \
    DateTimeField
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.dao.memberdao import MemberDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao
from juntagrico.mailer import adminnotification
from juntagrico.entity.subtypes import SubscriptionType
from juntagrico.models import Member, Subscription
from juntagrico.util.management import cancel_share
from juntagrico.util.temporal import next_membership_end_date


class Slider(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, template='forms/slider.html', css_class='slider', **kwargs)


class JuntagricoDateWidget(DateInput):
    """ Widget using browsers date picker
    """
    input_type = 'date'

    def format_value(self, value):
        if isinstance(value, str):
            return value
        return value.strftime('%Y-%m-%d')


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


class AbstractMemberCancellationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {
            'onSubmit': "return confirm('" + _('Möchtest du deine Mitgliedschaft verbindlich künden?') + "')"}
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'


class NonCoopMemberCancellationForm(AbstractMemberCancellationForm):
    class Meta:
        model = Member
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            FormActions(
                Submit('submit', _('Mitgliedschaft künden'), css_class='btn-success'),
            ),
        )

    def save(self, commit=True):
        today = datetime.date.today()
        self.instance.end_date = today
        self.instance.cancellation_date = today
        # if member has cancelled but not yet paid back share, can't deactivate member yet.
        if not self.instance.is_cooperation_member:
            self.instance.deactivation_date = today
        if (sub := self.instance.subscription_current) is not None:
            self.instance.leave_subscription(sub)
        if (sub := self.instance.subscription_future) is not None:
            self.instance.leave_subscription(sub)
        super().save(commit)


class CoopMemberCancellationForm(AbstractMemberCancellationForm):
    message = CharField(label=_('Mitteilung'), widget=Textarea, required=False)

    class Meta:
        model = Member
        fields = ['iban', 'addr_street', 'addr_zipcode', 'addr_location']
        labels = {
            "addr_street": _("Strasse/Nr.")
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'message', Fieldset(
                _('Bitte hinterlege oder überprüfe deine Daten, damit deine {} ausbezahlt werden können.').format(Config.vocabulary('share_pl')),
                'iban', 'addr_street', 'addr_zipcode', 'addr_location'),
            FormActions(
                Submit('submit', _('Mitgliedschaft künden'), css_class='btn-success'),
            ),
        )

    def clean_iban(self):
        # require IBAN on cancellation
        if self.data['iban'] == '':
            raise ValidationError(_('IBAN ist nicht gültig'))
        return self.data['iban']

    def save(self, commit=True):
        today = datetime.date.today()
        end_date = next_membership_end_date()
        self.instance.end_date = end_date
        self.instance.cancellation_date = today
        adminnotification.member_canceled(self.instance, end_date, self.data['message'])
        [cancel_share(s, today, end_date) for s in self.instance.share_set.all()]
        super().save(commit)


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
            ).format('<a href="mailto:{0}">{0}</a>'.format(Config.contacts('for_members')))
        )


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


class RegisterMemberForm(MemberBaseForm):
    comment = CharField(required=False, max_length=4000, label='Kommentar', widget=Textarea(attrs={"rows": 3}))
    agb = BooleanField(required=True)

    documents = {
        'die Statuten': Config.bylaws,
        'das Betriebsreglement': Config.business_regulations,
        'die DSGVO Infos': Config.gdpr_info,
    }
    text = {
        'accept_with_docs': _('Ich habe {} gelesen und erkläre meinen Willen, "{}" beizutreten. Hiermit beantrage ich meine Aufnahme.'),
        'accept_wo_docs': _('Ich erkläre meinen Willen, "{}" beizutreten. Hiermit beantrage ich meine Aufnahme.'),
        'and': _('und')
    }

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

    @classmethod
    def agb_label(cls):
        documents_html = []
        for text, link in cls.documents.items():
            if link().strip():
                documents_html.append('<a target="_blank" href="{}">{}</a>'.format(link(), _(text)))
        if documents_html:
            return cls.text['accept_with_docs'].format(
                (' ' + cls.text['and'] + ' ').join(documents_html),
                Config.organisation_long_name()
            )
        else:
            return cls.text['accept_wo_docs'].format(Config.organisation_long_name())


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
                    '<a href="mailto:{0}">{0}</a>'.format(Config.contacts('for_subscriptions')),
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
                LinkButton(_("Abbrechen"), reverse("subscription-landing")),
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


class SubscriptionTypeOption(Div):
    template = 'forms/subscription_type_option.html'

    def __init__(self, name, *args, instance, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        self.value = instance.id
        self.name = name

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        template = self.get_template_name(template_pack)
        return render_to_string(template, {"type": self.instance, "option": self})


class SubscriptionPartBaseForm(Form):
    def __init__(self, *args, product_method=SubscriptionProductDao.get_visible_normal_products, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self._product_method = product_method

    def get_type_field(self, subscription_type):
        field_name = f'amount[{subscription_type.id}]'
        self.fields[field_name] = IntegerField(label=subscription_type.name, min_value=0,
                                               initial=self._get_initial(subscription_type))
        return SubscriptionTypeField(field_name, instance=subscription_type)

    def _collect_type_fields(self):
        containers = []
        for product in self._product_method().all():
            product_container = CategoryContainer(instance=product)
            for subscription_size in product.sizes.filter(visible=True).exclude(types=None):
                size_container = CategoryContainer(instance=subscription_size, name=subscription_size.long_name)
                for subscription_type in subscription_size.types.filter(visible=True):
                    if (type_field := self.get_type_field(subscription_type)) is not None:
                        size_container.append(type_field)
                product_container.append(size_container)
            if len(product_container):
                containers.append(product_container)
        return containers

    def _get_initial(self, subscription_type):
        return 0

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


class SubscriptionPartChangeForm(SubscriptionPartBaseForm):
    part_type = ChoiceField()

    def __init__(self, part=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.part = part
        self.fields['part_type'].choices = self.get_choices
        self.helper.label_class = ''
        self.helper.field_class = 'col-md-12'
        self.helper.layout = Layout(
            *self._collect_type_fields(),
            FormActions(
                Submit('submit', _('Ändern'), css_class='btn-success')
            )
        )

    def get_type_field(self, subscription_type):
        if subscription_type.pk == self.part.type.pk:
            return None
        return SubscriptionTypeOption('part_type', instance=subscription_type)

    def get_choices(self):
        for subscription_type in SubscriptionTypeDao.get_normal_visible().exclude(pk=self.part.type.pk):
            yield subscription_type.id, subscription_type.name

    def clean(self):
        selected = self.cleaned_data.get('part_type')
        if selected:
            sub_type = SubscriptionType.objects.get(id=selected)
            # check if members in subscription have sufficient shares
            additional_available_shares = self.part.subscription.all_shares - self.part.subscription.required_shares
            additional_required_shares = sub_type.shares - self.part.type.shares
            if additional_available_shares < additional_required_shares:
                share_error_message = mark_safe(_('Es sind zu wenig {} vorhanden für diesen Bestandteil!{}').format(
                    Config.vocabulary('share_pl'),
                    '<br/><a href="{}" class="alert-link">{}</a>'.format(
                        reverse('manage-shares'), _('&rarr; Bestelle hier mehr {}').format(Config.vocabulary('share_pl')))
                ))
                raise ValidationError(share_error_message, code='share_error')
        else:
            # re-raise field error as form error
            for error_code, error in self.errors.items():
                raise ValidationError(error, code=error_code)
        return super().clean()


class NicknameForm(Form):
    nickname = CharField(label=_('{}-Spitzname').format(Config.vocabulary('subscription')), max_length=30, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Speichern')))


class GenerateListForm(Form):
    for_date = DateField(initial=datetime.date.today, label=_('Stichtag'), widget=JuntagricoDateWidget)
    future = BooleanField(label=_('Akzeptiere alle Depot-Änderungen'), required=False,
                          help_text=format_lazy('<a href="{}">{}</a>', reverse_lazy("manage-sub-depot-changes"), _('Änderungen stattdessen einzeln prüfen und akzeptieren')))

    def __init__(self, *args, **kwargs):
        show_future = kwargs.pop('show_future', False)
        super().__init__(*args, **kwargs)
        if not show_future:
            del self.fields['future']
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Listen Erzeugen')))


class ShiftTimeForm(Form):
    hours = FloatField(label=_('Stunden'))
    start = DateTimeField(label=_('Ab'), required=False, help_text='YYYY-MM-DD HH:MM')
    end = DateTimeField(label=_('Bis'), required=False, help_text='YYYY-MM-DD HH:MM')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Zeiten verschieben')))
