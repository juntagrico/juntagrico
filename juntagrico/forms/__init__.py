import datetime
from functools import cached_property

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, HTML, Layout, Submit, Fieldset, Div
from crispy_forms.utils import TEMPLATE_PACK
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import DateInput, forms, Form, CharField, PasswordInput, ModelForm, Textarea, BooleanField, \
    IntegerField, HiddenInput, ChoiceField, DateField, FloatField, DateTimeField
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import gettext as _, gettext_lazy
from djrichtextfield.widgets import RichTextWidget

from juntagrico.config import Config
from juntagrico.dao.memberdao import MemberDao
from juntagrico.entity.jobs import ActivityArea
from juntagrico.entity.member import Member
from juntagrico.entity.subs import SubscriptionPart, Subscription
from juntagrico.entity.subtypes import SubscriptionType, SubscriptionCategory
from juntagrico.mailer import adminnotification, membernotification
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
            if sub.primary_member != self.instance:
                self.instance.leave_subscription(sub)
        if (sub := self.instance.subscription_future) is not None:
            if sub.primary_member != self.instance:
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


class StartDateForm(ModelForm):
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

    def render(self, form, context, template_pack=TEMPLATE_PACK, **kwargs):
        template = self.get_template_name(template_pack)
        return render_to_string(template, {
            'type': self.instance,
            'option': self,
            'vocabulary': context['vocabulary']
        })


class SubscriptionPartBaseForm(ExtendableFormMixin, Form):
    def __init__(self, *args, extra=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.extra = extra

    def get_type_field(self, subscription_type):
        field_name = f'amount[{subscription_type.id}]'
        self.fields[field_name] = IntegerField(label=subscription_type.name, min_value=0,
                                               initial=self._get_initial(subscription_type))
        return SubscriptionTypeField(field_name, instance=subscription_type)

    def _collect_type_fields(self):
        containers = []
        for category in SubscriptionCategory.objects.exclude(bundles=None):
            category_container = CategoryContainer(instance=category)
            for bundle in category.bundles.exclude(types=None):
                bundle_container = CategoryContainer(instance=bundle, name=bundle.long_name)
                for subscription_type in self.type_filter(bundle.types):
                    if (type_field := self.get_type_field(subscription_type)) is not None:
                        bundle_container.append(type_field)
                if len(bundle_container):
                    category_container.append(bundle_container)
            if len(category_container):
                containers.append(category_container)
        return containers

    def type_filter(self, qs):
        return qs.filter(visible=True, is_extra=self.extra)

    def _get_initial(self, subscription_type):
        return 0

    def get_selected(self):
        return {
            sub_type: getattr(self, 'cleaned_data', {}).get('amount[' + str(sub_type.id) + ']', 0)
            for sub_type in SubscriptionType.objects.all()
        }


class SubscriptionPartSelectForm(SubscriptionPartBaseForm):
    no_selection_template = 'juntagrico/subscription/create/form/no_subscription_field.html'

    def __init__(self, selected, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected = selected
        self.containers = self._collect_type_fields()
        self.fields['no_selection'] = BooleanField(label=_('Kein {}').format(Config.vocabulary('subscription')),
                                                      initial=not any(selected.values()), required=False)
        self.helper.layout = self.get_form_layout()

    def get_form_layout(self):
        return Layout(
            *self.containers,
            Field('no_selection', template=self.no_selection_template),
            FormActions(
                Submit('submit', _('Weiter'), css_class='btn-success'),
                LinkButton(_('Abbrechen'), reverse('cs-cancel'))
            )
        )

    def _get_initial(self, subscription_type):
        return self.selected.get(str(subscription_type.id), 0)


class SubscriptionExtraPartSelectForm(SubscriptionPartSelectForm):
    no_selection_template = 'juntagrico/subscription/create/form/no_extras_field.html'

    def __init__(self, selected, *args, **kwargs):
        super().__init__(selected, *args, extra=True, **kwargs)


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
        self.pre_check(part)
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

    @staticmethod
    def pre_check(part):
        if part.subscription.canceled or part.subscription.inactive:
            raise Http404("Can't change subscription part of canceled subscription")
        if not SubscriptionType.objects.can_change():
            raise Http404("Can't change subscription part if there is only one subscription type")

    def get_type_field(self, subscription_type):
        return SubscriptionTypeOption('part_type', instance=subscription_type)

    def type_filter(self, qs):
        return super().type_filter(qs).exclude(pk=self.part.type.pk)

    def get_choices(self):
        for subscription_type in self.type_filter(SubscriptionType.objects.normal().visible()):
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

    def save(self):
        subscription_type = get_object_or_404(SubscriptionType, id=self.cleaned_data['part_type'])
        if self.part.activation_date is None:
            # just change type of waiting part
            self.part.type = subscription_type
            self.part.save()
        else:
            # cancel existing part and create new waiting one
            with transaction.atomic():
                new_part = SubscriptionPart.objects.create(subscription=self.part.subscription, type=subscription_type)
                self.part.cancel()
            self.send_notification(new_part)
        return self.part

    def send_notification(self, new_part):
        # notify admin
        adminnotification.subpart_canceled(self.part)
        adminnotification.subparts_created([new_part], self.part.subscription)


class SubscriptionPartContinueForm(SubscriptionPartChangeForm):
    def __init__(self, part=None, *args, **kwargs):
        super().__init__(part, *args, **kwargs)
        self.helper.layout = Layout(
            *self._collect_type_fields(),
            FormActions(
                Submit('submit', _('Bestellen'), css_class='btn-success')
            )
        )

    def type_filter(self, qs):
        return super().type_filter(qs).exclude(trial_days__gt=0)


class SubscriptionPartContinueByAdminForm(SubscriptionPartContinueForm):
    def send_notification(self, new_part):
        membernotification.trial_continued_for_you(self.part, new_part)
        pass


class TrialCloseoutForm(Form):
    deactivation_mode = ChoiceField(choices=(('by_end', ''), ('by_date', '')), required=False)
    deactivation_date = DateField(required=False)

    def __init__(self, part=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.part = part
        # add fields
        if self.follow_up_part or self.other_new_parts:
            self.fields['mode'] = ChoiceField(choices=(('append', ''), ('replace', '')), required=False)
            if self.follow_up_part:
                self.fields['activation_mode'] = ChoiceField(choices=(('next_day', ''), ('by_date', '')), required=False)
                self.fields['activation_date'] = DateField(required=False)
            for other_part in self.other_new_parts:
                self.fields[f'activate{other_part.id}'] = BooleanField(required=False)
                self.fields[f'activation_date{other_part.id}'] = DateField(required=False)

    @cached_property
    def follow_up_part(self):
        return self.part.follow_up_parts().waiting().filter(type__bundle=self.part.type.bundle).first()

    @cached_property
    def other_new_parts(self):
        other_parts = self.part.follow_up_parts().waiting()
        if self.follow_up_part:
            other_parts = other_parts.exclude(pk=self.follow_up_part.pk)
        return other_parts

    def clean(self):
        if self.cleaned_data.get('mode') != 'replace':
            if self.cleaned_data.get('deactivation_mode') == 'by_date':
                if self.cleaned_data.get('deactivation_date') is None:
                    raise ValidationError(_('Bitte gib ein Deaktivierungsdatum an.'), code='invalid_deactivation_date')
        if self.cleaned_data.get('mode') == 'append':
            if self.cleaned_data.get('activation_mode') == 'by_date':
                if self.cleaned_data.get('activation_date') is None:
                    raise ValidationError(_('Bitte gib ein Aktivierungsdatum an.'), code='invalid_activation_date')
        for other_part in self.other_new_parts:
            if self.cleaned_data.get(f'activate{other_part.id}'):
                if not self.cleaned_data.get(f'activation_date{other_part.id}'):
                    raise ValidationError(_('Bitte gib ein Aktivierungsdatum an.'), code='invalid_other_activation_date')

    def save(self):
        if self.cleaned_data.get('mode') == 'replace':
            self.follow_up_part.activate(self.part.activation_date)
            self.part.delete()
        else:
            # deactivate trial
            if self.cleaned_data.get('deactivation_mode') == 'by_end':
                self.part.deactivate(self.part.end_of_trial_date)
            elif self.cleaned_data.get('deactivation_mode') == 'by_date':
                self.part.deactivate(self.cleaned_data.get('deactivation_date'))
        if self.cleaned_data.get('mode') == 'append':
            # activate follow up part
            if self.cleaned_data.get('activation_mode') == 'next_day':
                self.follow_up_part.activate(self.part.end_of_trial_date + datetime.timedelta(days=1))
            elif self.cleaned_data.get('activation_mode') == 'by_date':
                self.follow_up_part.activate(self.cleaned_data.get('activation_date'))
        # activate other new parts
        for other_part in self.other_new_parts:
            if self.cleaned_data.get(f'activate{other_part.id}'):
                other_part.activate(self.cleaned_data.get(f'activation_date{other_part.id}'))
        return self.part


class ShareOrderForm(Form):
    field_template = 'forms/share_field.html'
    text = dict(
        member_info='Du brauchst als HauptbezieherIn mindestens {0} {1}.',
        member_existing='Du hast bereits {0} {1}.',
        co_member_info='Besitzt bereits {0} {1}.',
        form_error='Du brauchst insgesamt {0} {1} für die von dir gewählten {2}-Bestandteile'
    )

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-3'
    helper.field_class = 'col-md-3'

    def __init__(self, required, existing=0, co_members=None, *args, **kwargs):
        """
        :param required: number of shares that are required (for the subscriptions)
        :param existing: number of shares that the member already has
        :param co_members: an iterable of (name, existing_share_count) of co-members
        """
        super().__init__(*args, **kwargs)
        self.required = required
        self.existing = existing
        self.co_members = co_members or []
        required_shares = Config.required_shares()
        self.remaining = max(required_shares - existing, 0)

        # build share field for member
        v_share = Config.vocabulary('share') if required_shares == 1 else Config.vocabulary('share_pl')
        help_text = _(self.text['member_info']).format(required_shares, v_share)
        if existing:
            v_share = Config.vocabulary('share') if existing == 1 else Config.vocabulary('share_pl')
            help_text = _(self.text['member_existing']).format(required_shares, v_share)
        self.fields['of_member'] = IntegerField(
            label=_('Neue {}').format(Config.vocabulary('share_pl')), required=False,
            initial=self.remaining, min_value=self.remaining,
            help_text=help_text
        )

        # build share fields for co-members
        for i, co_member in enumerate(self.co_members):
            name = co_member[0]
            existing_shares = co_member[1]
            v_share = Config.vocabulary('share') if existing_shares == 1 else Config.vocabulary('share_pl')
            help_text = _(self.text['co_member_info']).format(existing_shares, v_share)
            self.fields[f'of_co_member[{i}]'] = IntegerField(
                label=name, initial=0, min_value=0,
                help_text=help_text
            )

        self.helper.layout = Layout(
            Field('of_member', template=self.field_template),
            *[Field(f'of_co_member[{i}]', template=self.field_template) for i in range(len(self.co_members))],
            FormActions(
                Submit('submit', _('Weiter'), css_class='btn-success'),
                HTML('<a href="{0}" class="btn">{1}</a>'.format(reverse('cs-cancel'), _("Abbrechen")))
            )
        )

    def clean(self):
        total_required = max(self.required, Config.required_shares())
        total_existing = max(0, self.existing + sum(dict(self.co_members).values()))
        remaining_required = max(0, total_required - total_existing)
        # count new shares
        of_member = self.cleaned_data.get('of_member', 0)
        of_co_member = sum([self.cleaned_data.get(f'of_co_member[{i}]', 0) for i in range(len(self.co_members))])
        # evaluate
        if of_member + of_co_member < remaining_required:
            raise ValidationError(_(self.text['form_error']).format(
                total_required,
                Config.vocabulary('share') if total_required == 1 else Config.vocabulary('share_pl'),
                Config.vocabulary('subscription')
            ))


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


class AreaDescriptionForm(ModelForm):
    class Meta:
        model = ActivityArea
        fields = ['description']
        labels = {'description': ''}
        if Config.using_richtext():
            widgets = {'description': RichTextWidget()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            'description',
            FormActions(
                Submit('submit', _('Speichern')),
            ),
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
