import datetime

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django import forms
from django.db.models import Exists, OuterRef
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext

from juntagrico.config import Config
from juntagrico.entity.member import SubscriptionMembership
from juntagrico.entity.membership import Membership
from juntagrico.entity.subs import Subscription
from juntagrico.forms import HorizontalFormMixin, JuntagricoDateWidget
from juntagrico.mailer import membernotification
from juntagrico.util import temporal


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


class CancellationField(forms.ChoiceField):
    widget = forms.RadioSelect

    def __init__(self, keep=False, *args, **kwargs):
        label = kwargs.pop('label', _('Auf wann möchtest du {this_subscription_acc} kündigen?').format(
            this_subscription_acc=Config.vocabulary('this_subscription_acc')
        ),)

        choices = [
            ('regular', mark_safe(_('auf den nächsten regulären Termin: {date}').format(
                date=f'<strong>{date_format(temporal.next_cancelation_date())}</strong>'
            ))),
            ('asap', _('so bald wie möglich')),
        ]
        if keep:
            choices += [
                ('keep', _('{this_subscription_acc} behalten').format(
                    this_subscription_acc=Config.vocabulary('this_subscription_acc')
                )),
            ]

        initial = kwargs.pop('initial', 'regular')
        super().__init__(*args, choices=choices, label=label, initial=initial, **kwargs)

    def clean(self, value):
        choice = super().clean(value)
        if choice == 'asap':
            return datetime.date.today()
        if choice == 'regular':
            return temporal.next_cancelation_date()
        return None


class CancellationForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = []

    cancellation = CancellationField()
    comment = forms.CharField(
        label=_('Möchtest du noch etwas loswerden?'),
        required=False,
        widget=forms.Textarea,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    def save(self, commit=True):
        # cancel subscriptions
        end_date = self.cleaned_data['cancellation']
        if end_date is not None:
            self.instance.cancel(end_date=end_date, message=self.cleaned_data.get('comment'))


class LeaveForm(forms.ModelForm):
    class Meta:
        model = SubscriptionMembership
        fields = []

    leave_date = forms.DateField(
        label=_('Auf wann möchtest du {this_subscription_acc} verlassen?').format(this_subscription_acc=Config.vocabulary('this_subscription_acc')),
        widget=JuntagricoDateWidget,
        initial=datetime.date.today,
    )
    comment = forms.CharField(
        label=_('Mitteilung an {subscription}-Verwalter:in ').format(subscription=Config.vocabulary('subscription')),
        required=False,
        widget=forms.Textarea,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    def get_subscription_fields(self):
        return [self['leave_date']]

    def save(self, commit=True):
        # leave subscription
        primary_member = self.instance.subscription.primary_member
        member = self.instance.member
        self.instance.leave(on_date=self.cleaned_data['leave_date'])
        membernotification.co_member_left_subscription(primary_member, member, self.cleaned_data.get('comment'))
