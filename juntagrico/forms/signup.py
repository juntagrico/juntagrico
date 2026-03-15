from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Submit, Field
from django import forms
from django.utils.html import format_html_join, format_html
from django.utils.translation import gettext_lazy

from . import HorizontalFormMixin, ShareOrderForm
from ..config import Config


class MembershipForm(HorizontalFormMixin, forms.Form):
    membership = forms.BooleanField()

    documents = [
        (gettext_lazy('die Statuten'), Config.bylaws),
    ]
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
    def get_label(cls):
        documents_html = format_html_join(
            ' ' + cls.text['and'] + ' ',
            '<a target="_blank" href="{}">{}</a>',
            ((link(), text) for text, link in cls.documents if link().strip())
        )
        if documents_html:
            return format_html(
                str(cls.text['accept_with_docs']), documents=documents_html, organization=Config.organisation_long_name()
            )
        else:
            return cls.text['accept_wo_docs'].format(organization=Config.organisation_long_name())


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
