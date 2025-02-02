import datetime

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, HTML, Div, Fieldset
from crispy_forms.utils import TEMPLATE_PACK
from django.db import transaction
from django.forms import CharField, PasswordInput, Form, ValidationError, \
    ModelForm, DateInput, IntegerField, BooleanField, HiddenInput, Textarea, ChoiceField, DateField, FloatField, \
    DateTimeField, forms
from django.template.loader import render_to_string, get_template
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from juntagrico.config import Config
from juntagrico.dao.memberdao import MemberDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao
from juntagrico.entity.jobs import Assignment, Job, JobExtra
from juntagrico.entity.subtypes import SubscriptionType
from juntagrico.models import Member, Subscription
from juntagrico.signals import subscribed, assignment_changed
from juntagrico.util.temporal import get_business_year, get_business_date_range


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


class ExtendableFormMetaclass(forms.DeclarativeFieldsMetaclass):
    def __getattr__(cls, name):
        if name == 'validators':
            cls.validators = []
            return cls.validators
        raise AttributeError(name)


class ExtendableFormMixin(metaclass=ExtendableFormMetaclass):
    """
    Allows adding validators to the form like this:
    SomeForm.validators.append(some_validator_function)
    """
    def get_validators(self):
        return getattr(self, 'validators', [])

    def clean(self):
        for validator in self.get_validators():
            validator(self)
        return super().clean()


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
    message = CharField(label=_('Mitteilung'), widget=Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {
            'onSubmit': "return confirm('" + _('Möchtest du deine Mitgliedschaft verbindlich künden?') + "')"}
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            'message',
            FormActions(
                Submit('submit', _('Mitgliedschaft künden'), css_class='btn-danger'),
            ),
        )

    def save(self, commit=True):
        if (sub := self.instance.subscription_current) is not None:
            self.instance.leave_subscription(sub)
        if (sub := self.instance.subscription_future) is not None:
            self.instance.leave_subscription(sub)
        self.instance.cancel()
        return super().save(commit)


class NonCoopMemberCancellationForm(AbstractMemberCancellationForm):
    class Meta:
        model = Member
        fields = []


class CoopMemberCancellationForm(AbstractMemberCancellationForm):
    class Meta:
        model = Member
        fields = ['iban', 'addr_street', 'addr_zipcode', 'addr_location']
        labels = {
            "addr_street": gettext_lazy("Strasse/Nr.")
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.insert(1, Fieldset(
            _('Bitte hinterlege oder überprüfe deine Daten, damit deine {} ausbezahlt werden können.').format(Config.vocabulary('share_pl')),
            'iban', 'addr_street', 'addr_zipcode', 'addr_location')
        )

    def clean_iban(self):
        # require IBAN on cancellation
        if self.data['iban'] == '':
            raise ValidationError(_('IBAN ist nicht gültig'))
        return self.data['iban']


class MemberProfileForm(ModelForm):
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email',
                  'addr_street', 'addr_zipcode', 'addr_location',
                  'birthday', 'phone', 'mobile_phone', 'iban', 'reachable_by_email']
        labels = {
            "phone": gettext_lazy("Telefonnummer"),
            "email": gettext_lazy("E-Mail-Adresse"),
            "birthday": gettext_lazy("Geburtstag"),
            "addr_street": gettext_lazy("Strasse/Nr."),
            "reachable_by_email": gettext_lazy(
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
                Submit('submit', _('Speichern'), css_class='btn-success'),
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
            "phone": gettext_lazy("Telefonnummer"),
            "email": gettext_lazy("E-Mail-Adresse"),
            "birthday": gettext_lazy("Geburtstag"),
            "addr_street": gettext_lazy("Strasse/Nr."),
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
    comment = CharField(required=False, max_length=4000, label=gettext_lazy('Kommentar'), widget=Textarea(attrs={"rows": 3}))
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
                                            .format(Config.vocabulary('co_member_pl'))), 'email_exists')
        existing_member = MemberDao.member_by_email(email)
        if existing_member:
            if existing_member.blocked:
                raise ValidationError(mark_safe(escape(_('Die Person mit dieser E-Mail-Adresse ist bereits aktive '
                    '{}-BezierIn. Bitte meldet euch bei {}, wenn ihr bestehende {} als {} hinzufügen möchtet.')).format(
                    Config.vocabulary('subscription'),
                    '<a href="mailto:{0}">{0}</a>'.format(Config.contacts('for_subscriptions')),
                    Config.vocabulary('member_type_pl'),
                    Config.vocabulary('co_member_pl')
                )), 'has_active_subscription')
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


class SubscriptionPartBaseForm(ExtendableFormMixin, Form):
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
        # check that subscription is not canceled:
        if self.subscription.cancellation_date:
            raise ValidationError(_('Für gekündigte {} können keine Bestandteile oder Zusatzabos bestellt werden').
                                  format(Config.vocabulary('subscription_pl')), code='no_order_if_canceled')
        # check if members in subscription have sufficient shares
        if Config.enable_shares():
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
            if Config.enable_shares():
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
                HTML(get_template('messages/job_assigned.html').render(dict(amount=self.current_slots - 1))),
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


class ShiftTimeForm(Form):
    hours = FloatField(label=_('Stunden'))
    start = DateTimeField(label=_('Ab'), required=False, help_text='YYYY-MM-DD HH:MM')
    end = DateTimeField(label=_('Bis'), required=False, help_text='YYYY-MM-DD HH:MM')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Zeiten verschieben')))


class DateWidget(DateInput):
    """ Widget using browsers date picker
    """
    input_type = 'date'

    def format_value(self, value):
        if isinstance(value, str):
            return value
        return value.strftime('%Y-%m-%d')


class DateRangeForm(Form):
    start_date = DateField(label=_('Von'), widget=DateWidget())
    end_date = DateField(label=_('Bis'), widget=DateWidget())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.label_class = 'mr-2'
        self.helper.field_class = 'mr-2'
        self.helper.add_input(Submit('submit', _('Anwenden')))


class BusinessYearForm(Form):
    year = ChoiceField(label=_('Saison'), required=False)

    def __init__(self, min_date, max_date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['year'].choices = self.get_choices(min_date, max_date)
        # default to current business year
        if not self.data.get('year'):
            self.data = {'year': get_business_year()}
        # build form
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.label_class = 'mr-2'
        self.helper.field_class = 'mr-2'
        self.helper.add_input(Submit('submit', _('Anzeigen')))

    @staticmethod
    def get_choices(min_date, max_date):
        """ returns choices with each business year from min_date or max_date
        :param min_date: date to start range from, defaults to today
        :param max_date: date to end range, defaults to today
        :return: list of tuples (year, label)
        """
        today = datetime.date.today()
        min_date = min_date or today
        max_date = max_date or today
        business_year = Config.business_year_start()
        if business_year["day"] == 1 and business_year["month"] == 1:
            choices = [
                (year, str(year))
                for year in range(min_date.year, max(today.year, max_date.year) + 1)
            ]
        else:
            choices = [
                (year, f"{year}/{year + 1}")
                for year in range(
                    get_business_year(min_date),
                    get_business_year(max(today, max_date)) + 1,
                )
            ]
        return choices

    def date_range(self):
        return get_business_date_range(int(self.cleaned_data.get('year')))
