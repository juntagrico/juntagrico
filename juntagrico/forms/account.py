import datetime

from crispy_forms.helper import FormHelper
from django.db.models import F
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _, gettext, ngettext

from django import forms

from juntagrico.config import Config
from juntagrico.entity.member import Member
from juntagrico.forms import JuntagricoDateWidget
from juntagrico.util import temporal


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
    comment = forms.CharField(
        label=_('Möchtest du noch etwas loswerden?'),
        required=False,
        widget=forms.Textarea,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.primary_subscriptions = self.instance.subscription_primary.not_terminated()
        for subscription in self.primary_subscriptions:
            self.fields[f'primary_subscription_{subscription.id}'] = forms.ChoiceField(
                label=_('Auf wann möchtest du diese/n/s {subscription} kündigen?').format(
                    subscription=Config.vocabulary('subscription')
                ),
                widget=forms.RadioSelect,
                choices=self.get_subscription_choices(),
                initial='regular',
            )
        self.co_memberships = (
            self.instance.subscriptions
            .filter(subscriptionmembership__leave_date=None)
            .exclude(primary_member=self.instance)
            .order_by(F('subscriptionmembership__join_date').asc(nulls_last=True))
        )
        for subscription in self.co_memberships:
            self.fields[f'co_membership_{subscription.id}'] = forms.TypedChoiceField(
                label='',
                widget=forms.RadioSelect,
                choices=[
                    (False, gettext('diese/n/s {subscription} verlassen').format(subscription=Config.vocabulary('subscription'))),
                    (True, gettext('diese/n/s {subscription} behalten').format(subscription=Config.vocabulary('subscription'))),
                ],
                initial=False,
                coerce=choice_to_bool,
            )
            self.fields[f'co_membership_date_{subscription.id}'] = forms.DateField(
                label=_('Auf wann möchtest du diese/n/s {subscription} verlassen?').format(subscription=Config.vocabulary('subscription')),
                widget=JuntagricoDateWidget,
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
            self.fields['iban'].required = (
                    not self.data
                    or int(self.data.get('shares', 0)) > 0
                    or self.data.get('primary_subscription') == 'asap'
            )
        except ValueError:
            self.fields['iban'].required = True
        areas = self.instance.areas.all()
        self.fields['activity_areas'].queryset = areas
        self.fields['activity_areas'].initial = areas.values_list('id', flat=True)
        self.helper = FormHelper()

    def get_subscription_choices(self):
        return [
            ('regular', mark_safe(_('auf den nächsten regulären Termin: {date}').format(
                date=f'<strong>{date_format(temporal.next_cancelation_date())}</strong>'
            ))),
            ('asap', _('so bald wie möglich')),
            ('keep', _('diese/n/s {subscription} behalten').format(subscription=Config.vocabulary('subscription'))),
        ]

    def get_primary_subscriptions_and_fields(self):
        for subscription in self.primary_subscriptions:
            yield subscription, self[f'primary_subscription_{subscription.id}']

    def get_co_memberships_and_fields(self):
        for subscription in self.co_memberships:
            yield subscription, {
                'keep': self[f'co_membership_{subscription.id}'],
                'date': self[f'co_membership_date_{subscription.id}'],
            }

    def clean(self):
        cleaned_data = super().clean()

        # membership required
        if cleaned_data.get('membership') is False:
            membership_required = any(
                cleaned_data[f'primary_subscription_{s.id}'] == 'keep' and s.requires_membership
                for s in self.primary_subscriptions
            )
            if membership_required:
                self.add_error(
                    'membership',
                    capfirst(gettext('{membership} wird noch für ein/e {subscription} benötigt.').format(
                        membership=Config.vocabulary('membership'),
                        subscription=Config.vocabulary('subscription'),
                    ))
                )

        # shares required
        remaining_shares = 0
        if Config.enable_shares():
            usable_shares = self.usable_shares.count()
            remaining_shares = usable_shares - cleaned_data.get('shares', 0)
            if Config.membership('enable'):
                required_for_membership = Config.membership('required_shares')
                if remaining_shares < required_for_membership:
                    self.add_error(
                        'shares',
                        ngettext(
                            'Es werden noch {num} {share} für den/die/das {membership} benötigt.',
                            'Es werden noch {num} {shares} für den/die/das {membership} benötigt.',
                            required_for_membership
                        ).format(
                            num=required_for_membership,
                            membership=Config.vocabulary('membership'),
                            share=Config.vocabulary('share'),
                            shares=Config.vocabulary('share_pl'),
                        )
                    )
            required_for_subscription = usable_shares - max(
                *(
                    s.share_overflow
                    for s in self.primary_subscriptions
                    if cleaned_data[f'primary_subscription_{s.id}'] == 'keep'
                ),
                *(
                    s.share_overflow
                    for s in self.co_memberships
                    if cleaned_data[f'co_membership_{s.id}'] is True
                ),
                0
            )
            if remaining_shares < required_for_subscription:
                self.add_error(
                    'shares',
                    ngettext(
                        'Es werden noch {num} {share} für den/die/das {subscription} benötigt.',
                        'Es werden noch {num} {shares} für den/die/das {subscription} benötigt.',
                        required_for_subscription
                    ).format(
                        num=required_for_subscription,
                        subscription=Config.vocabulary('subscription'),
                        share=Config.vocabulary('share'),
                        shares=Config.vocabulary('share_pl'),
                    )
                )

        # account required
        account_required = remaining_shares or cleaned_data.get('membership') is True or any(
            cleaned_data[f'primary_subscription_{s.id}'] == 'keep'
            for s in self.primary_subscriptions
        ) or any(
            cleaned_data[f'co_membership_{s.id}'] is True
            for s in self.co_memberships
        )
        if account_required:
            self.add_error('account', gettext('Zuerst muss alles andere gekündigt werden.'))

    def save(self, commit=True):
        super().save(commit=commit)
        comment = self.cleaned_data['comment']

        # cancel subscriptions
        for subscription in self.primary_subscriptions:
            choice = self.cleaned_data[f'primary_subscription_{subscription.id}']
            if choice == 'asap':
                cancel_date = datetime.date.today()
            elif choice == 'regular':
                cancel_date = temporal.next_cancelation_date()
            else:  # keep subscription
                continue
            subscription.cancel(end_date=cancel_date, message=comment)

        # leave subscriptions
        for co_membership in self.co_memberships:
            if self.cleaned_data[f'co_membership_{co_membership.id}'] is False:
                self.instance.leave_subscription(
                    subscription=co_membership,
                    changedate=self.cleaned_data[f'co_membership_date_{co_membership.id}']
                )

        # leave activity areas
        for activity_area in self.instance.areas.exclude(pk__in=self.cleaned_data['activity_areas']):
            activity_area.leave(self.instance)

        # cancel membership
        if Config.membership('enable') and self.cleaned_data['membership'] is False:
            for membership in self.memberships:
                membership.cancel()

        # cancel shares
        if Config.enable_shares():
            for share in self.usable_shares()[:self.cleaned_data['shares']]:
                share.cancel()

        # cancel account
        if self.cleaned_data['account'] is False:
            self.instance.cancel()
