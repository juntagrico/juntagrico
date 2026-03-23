from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Submit, Layout
from django import forms
from django.db.models import Exists, OuterRef
from django.utils.translation import gettext_lazy as _, gettext

from juntagrico.config import Config
from juntagrico.entity.membership import Membership
from juntagrico.entity.subs import Subscription
from juntagrico.forms import HorizontalFormMixin


class PrimaryMemberChangeForm(HorizontalFormMixin, forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['primary_member']
        labels = {
            'primary_member': _('Neue:r {subscription}-Verwalter:in').format(subscription=Config.vocabulary('subscription')),
        }
        help_texts = {
            'primary_member': ''
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        co_members = self.instance.co_members()
        if Config.membership('enable') and self.instance.requires_membership:
            co_members = co_members.filter(Exists(Membership.objects.filter(account=OuterRef('id')).not_canceled()))
        self.fields['primary_member'].queryset = co_members
        self.fields['primary_member'].required = True

        self.helper.layout = Layout(
            'primary_member',
            FormActions(
                Submit(
                    'submit',
                    gettext('{subscription} übergeben').format(
                        subscription=Config.vocabulary('subscription')
                    ),
                    css_class='btn-success'
                ),
            ),
        )
