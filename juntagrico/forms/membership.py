import datetime

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from django import forms
from django.utils.html import format_html_join, format_html
from django.utils.translation import gettext_lazy

from . import HorizontalFormMixin, ShareOrderForm, JuntagricoDateWidget
from ..config import Config
from ..entity.membership import Membership
from ..mailer import adminnotification, membernotification
from ..util.management import create_share


class MembershipForm(HorizontalFormMixin, forms.Form):
    membership = forms.BooleanField()

    text = {
        'accept_with_docs': gettext_lazy(
            'Ich habe {documents} gelesen und erkläre meinen Willen, "{organization}" beizutreten. '
            'Hiermit beantrage ich meine Aufnahme.'
        ),
        'accept_wo_docs': gettext_lazy(
            'Ich erkläre meinen Willen, "{organization}" beizutreten. Hiermit beantrage ich meine Aufnahme.'
        ),
        'and': gettext_lazy('und'),
        'submit': gettext_lazy('Weiter'),
    }

    def __init__(self, required, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['membership'].required = required
        self.fields['membership'].label = self.get_label()

        self.helper.label_class = 'd-none'
        self.helper.field_class = 'col-md-12'
        self.helper.layout = Layout(
            'membership',
            FormActions(
                Submit('submit', str(self.text['submit']), css_class='btn-success'),
            )
        )

    @classmethod
    def get_documents(cls):
        return Config.documents('membership-signup-accept', True)

    @classmethod
    def get_label(cls):
        documents_html = format_html_join(
            ' ' + cls.text['and'] + ' ',
            '<a target="_blank" href="{1}">{0}</a>',
            cls.get_documents()
        )
        if documents_html:
            return format_html(
                str(cls.text['accept_with_docs']), documents=documents_html, organization=Config.organisation_long_name()
            )
        else:
            return cls.text['accept_wo_docs'].format(organization=Config.organisation_long_name())

    def save(self, account, comment=None):
        # if there is a membership that has not been deactivated yet, keep that one
        if membership := account.memberships.active_or_requested().first():
            membership.deactivation_date = None
            membership.cancellation_date = None
            membership.save()
        else:
            membership = Membership.objects.create(account=account)
        adminnotification.membership_created(membership, comment)


class CreateMembershipForm(MembershipForm):
    text = MembershipForm.text | {
        'submit': gettext_lazy('{membership} beantragen').format(membership=Config.vocabulary('membership')),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(True, *args, **kwargs)


class CreateMembershipWithSharesForm(ShareOrderForm, CreateMembershipForm):
    text = ShareOrderForm.text | CreateMembershipForm.text

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_class = ''
        self.helper.label_class = ''
        self.helper.field_class = ''
        self.helper.layout = Layout(
            Field('of_member', wrapper_class='w-50'),
            'membership',
            FormActions(
                Submit('submit', str(self.text['submit']), css_class='btn-success'),
            )
        )

    @classmethod
    def create(cls, required_shares, existing_shares):
        class BoundCreateMembershipWithSharesForm(CreateMembershipWithSharesForm):
            def __init__(self, *args, **kwargs):
                super().__init__(required_shares, existing_shares, *args, **kwargs)

        return BoundCreateMembershipWithSharesForm

    def save(self, account):
        if ordered_shares := self.cleaned_data.get('of_member'):
            create_share(account, ordered_shares)
        super().save(account)


class CancelAndDeactivateForm(forms.ModelForm):
    deactivate = forms.BooleanField(initial=False, required=False, label=gettext_lazy('Deaktivieren?'))
    membership_ids = forms.CharField(required=True, widget=forms.HiddenInput())

    class Meta:
        model = Membership
        fields = ('cancellation_date', 'deactivation_date')
        widgets = {
            'cancellation_date': JuntagricoDateWidget,
            'deactivation_date': JuntagricoDateWidget,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cancellation_date'].widget.attrs['max'] = datetime.date.today()
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'membership_ids',
            'cancellation_date',
            'deactivate',
            'deactivation_date',
        )

    def save(self, commit=True):
        instance = super().save(commit)
        if instance.deactivation_date is not None:
            membernotification.membership_deactivated(instance)
