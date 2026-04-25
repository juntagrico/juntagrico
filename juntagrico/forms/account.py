import datetime

from crispy_forms.helper import FormHelper
from django.core.exceptions import ValidationError
from django.db.models import F
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _, gettext, ngettext

from django import forms

from juntagrico import signals
from juntagrico.config import Config
from juntagrico.entity.member import Member
from juntagrico.forms import JuntagricoDateWidget
from juntagrico.forms.subscription import CancellationField
from juntagrico.mailer import adminnotification


def choice_to_bool(value):
    return value == 'True'


class CancellationForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['iban', 'addr_street', 'addr_zipcode', 'addr_location']
        labels = {
            "addr_street": _("Strasse/Nr.")
        }

    class Media:
        js = [
            'juntagrico/external/bootstrap-input-spinner.js',
            'juntagrico/js/forms/cancellationForm.js',
        ]

    activity_areas = forms.ModelMultipleChoiceField(
        label=_('In welchen Tätigkeitsbereichen möchtest du aktiv bleiben?'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=None
    )
    account = forms.TypedChoiceField(
        label='',
        widget=forms.RadioSelect,
        choices=[
            (False, _('{account} nach der Kündigung löschen').format(account=Config.vocabulary('member'))),
            (True, _('{account} behalten').format(account=Config.vocabulary('member'))),
        ],
        initial=False,
        coerce=choice_to_bool,
    )
    comment = forms.CharField(  # TODO: make sure comment is sent at least to 1 recipient.
        label=_('Möchtest du noch etwas loswerden?'),
        required=False,
        widget=forms.Textarea,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.primary_subscriptions = self.instance.subscription_primary.not_terminated()
        for subscription in self.primary_subscriptions:
            self.fields[f'primary_subscription_{subscription.id}'] = CancellationField(keep=True)

        self.co_memberships = (
            self.instance.subscriptionmembership_set
            .filter(leave_date=None)  # TODO: future leave date may exist. In that case user may want to leave earlier
            .exclude(subscription__primary_member=self.instance)
            .order_by(F('join_date').asc(nulls_last=True))
        )
        v_this_subscription_acc = Config.vocabulary('this_subscription_acc')
        for subscription_membership in self.co_memberships:
            if not subscription_membership.can_leave():
                continue
            self.fields[f'co_membership_{subscription_membership.id}'] = forms.TypedChoiceField(
                label='',
                widget=forms.RadioSelect,
                choices=[
                    (False, gettext('{this_subscription_acc} verlassen').format(this_subscription_acc=v_this_subscription_acc)),
                    (True, gettext('{this_subscription_acc} behalten').format(this_subscription_acc=v_this_subscription_acc)),
                ],
                initial=False,
                coerce=choice_to_bool,
            )
            self.fields[f'co_membership_date_{subscription_membership.id}'] = forms.DateField(
                label=_('Auf wann möchtest du {this_subscription_acc} verlassen?').format(this_subscription_acc=v_this_subscription_acc),
                widget=JuntagricoDateWidget,
                required=not self.data or self.data.get(f'co_membership_{subscription_membership.id}') == 'False',
                initial=datetime.date.today(),
            )

        if Config.membership('enable'):
            self.memberships = self.instance.memberships.not_canceled()
            if self.memberships.exists():
                self.fields['membership'] = forms.TypedChoiceField(
                    label='',
                    widget=forms.RadioSelect,
                    choices=[
                        (False, gettext('{membership} kündigen').format(membership=Config.vocabulary('membership'))),
                        (True, gettext('{membership} behalten').format(membership=Config.vocabulary('membership'))),
                    ],
                    initial=False,
                    coerce=choice_to_bool,
                )

        if Config.enable_shares():
            self.usable_shares = self.instance.shares.usable()
            if usable_share_count := self.usable_shares.count():
                self.fields['shares'] = forms.IntegerField(
                    label=gettext('Wie viele {shares} möchtest du kündigen?').format(shares=Config.vocabulary('share_pl')),
                    initial=usable_share_count,
                    max_value=usable_share_count,
                    min_value=0,
                )

        try:
            payment_details_required = (
                    not self.data
                    or int(self.data.get('shares', 0)) > 0
                    or self.data.get('primary_subscription') == 'asap'
            )
        except ValueError:
            payment_details_required = True
        for field in CancellationForm.Meta.fields:
            self.fields[field].required = payment_details_required

        areas = self.instance.areas.all()
        self.fields['activity_areas'].queryset = areas
        self.fields['activity_areas'].initial = areas.values_list('id', flat=True)
        self.helper = FormHelper()

    def get_primary_subscriptions_and_fields(self):
        for subscription in self.primary_subscriptions:
            yield subscription, self[f'primary_subscription_{subscription.id}']

    def get_co_memberships_and_fields(self):
        for subscription_membership in self.co_memberships:
            if f'co_membership_{subscription_membership.id}' in self.fields:
                yield subscription_membership.subscription, [
                    self[f'co_membership_{subscription_membership.id}'],
                    self[f'co_membership_date_{subscription_membership.id}'],
                ]
            else:
                yield subscription_membership.subscription, None

    def clean(self):
        cleaned_data = super().clean()

        changed = (
            any(cleaned_data.get(f'primary_subscription_{s.id}') is not None for s in self.primary_subscriptions)
            or any(cleaned_data.get(f'co_membership_{c.id}') is False for c in self.co_memberships)
            or cleaned_data.get('membership') is False
            or cleaned_data.get('shares', 0) > 0
            or cleaned_data.get('account') is False
        )
        if not changed:
            raise ValidationError(_('Wähle aus, was du kündigen möchtest'))

        # membership required
        if cleaned_data.get('membership') is False:
            membership_required = any(
                cleaned_data.get(f'primary_subscription_{s.id}') is None and s.requires_membership
                for s in self.primary_subscriptions
            )
            if membership_required:
                self.add_error(
                    'membership',
                    capfirst(gettext('{membership} wird noch für {your_subscription_acc} benötigt.').format(
                        membership=Config.vocabulary('membership'),
                        your_subscription_acc=Config.vocabulary('your_subscription_acc'),
                    ))
                )

        # shares required
        remaining_shares = 0
        if Config.enable_shares() and 'shares' in self.fields:
            usable_shares = self.usable_shares.count()
            remaining_shares = usable_shares - cleaned_data.get('shares', 0)
            if self.primary_subscriptions or self.co_memberships:
                required_for_subscription = max(
                    *(
                        s.share_overflow
                        for s in self.primary_subscriptions
                        if cleaned_data.get(f'primary_subscription_{s.id}') is None
                    ),
                    *(
                        s.subscription.share_overflow
                        for s in self.co_memberships
                        if cleaned_data.get(f'co_membership_{s.id}') is True
                    ),
                    0, 0
                )
                if remaining_shares < required_for_subscription:
                    self.add_error(
                        'shares',
                        ngettext(
                            'Es wird noch {num} {share} für {your_subscription_acc} benötigt.',
                            'Es werden noch {num} {shares} für {your_subscription_acc} benötigt.',
                            required_for_subscription
                        ).format(
                            num=required_for_subscription,
                            your_subscription_acc=Config.vocabulary('your_subscription_acc'),
                            share=Config.vocabulary('share'),
                            shares=Config.vocabulary('share_pl'),
                        )
                    )
            if Config.membership('enable') and cleaned_data.get('membership'):
                required_for_membership = Config.membership('required_shares')
                if remaining_shares < required_for_membership:
                    self.add_error(
                        'shares',
                        ngettext(
                            'Es wird noch {num} {share} für {your_membership_acc} benötigt.',
                            'Es werden noch {num} {shares} für {your_membership_acc} benötigt.',
                            required_for_membership
                        ).format(
                            num=required_for_membership,
                            your_membership_acc=Config.vocabulary('your_membership_acc'),
                            share=Config.vocabulary('share'),
                            shares=Config.vocabulary('share_pl'),
                        )
                    )

        # account required
        if cleaned_data.get('account') is False:
            account_required = remaining_shares or cleaned_data.get('membership') is True or any(
                cleaned_data.get(f'primary_subscription_{s.id}') is None
                for s in self.primary_subscriptions
            ) or any(
                cleaned_data.get(f'co_membership_{s.id}') is True
                for s in self.co_memberships
            )
            if account_required:
                self.add_error('account', gettext('Zuerst muss alles andere gekündigt werden.'))

    def save(self, commit=True):
        super().save(commit=commit)
        summary = {'subscription': [], 'co_membership': []}
        comment = self.cleaned_data.get('comment')

        # cancel subscriptions
        for subscription in self.primary_subscriptions:
            end_date = self.cleaned_data[f'primary_subscription_{subscription.id}']
            if end_date is not None:
                subscription.cancel(end_date=end_date, message=comment)
                summary['subscription'].append(subscription)

        # leave subscriptions
        for co_membership in self.co_memberships:
            if self.cleaned_data.get(f'co_membership_{co_membership.id}') is False:
                co_membership.leave(
                    on_date=self.cleaned_data[f'co_membership_date_{co_membership.id}']
                )
                summary['co_membership'].append(co_membership)

        # leave activity areas
        leave_areas = self.instance.areas.exclude(pk__in=self.cleaned_data['activity_areas'])
        for activity_area in leave_areas:
            activity_area.leave(self.instance)
        if leave_areas:
            summary['activity_area'] = leave_areas

        # cancel membership
        if Config.membership('enable') and self.cleaned_data.get('membership') is False:
            for membership in self.memberships:
                membership.cancel()
            adminnotification.membership_canceled(self.instance, comment)
            summary['membership'] = True

        # cancel shares
        if Config.enable_shares() and 'shares' in self.cleaned_data:
            cancel_shares = self.cleaned_data['shares']
            for share in self.usable_shares[:cancel_shares]:
                share.cancel()
            if cancel_shares > 0:
                summary['share'] = cancel_shares

        # cancel account
        if self.cleaned_data['account'] is False:
            self.instance.cancel()
            comment = self.cleaned_data.get('comment')
            adminnotification.member_canceled(self.instance, comment)
            signals.canceled.send(Member, instance=self.instance, message=comment)  # backwards compatibility
            summary['account'] = True

        return summary
