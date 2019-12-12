from django import forms
from django.contrib import admin

from juntagrico.dao.memberdao import MemberDao
from juntagrico.entity.subs import Subscription


# This form exists to restrict primary user choice to users that have actually set the
# current subscription as their subscription


class SubscriptionAdminForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = '__all__'

    subscription_members = forms.ModelMultipleChoiceField(queryset=MemberDao.all_members(), required=False,
                                                          widget=admin.widgets.FilteredSelectMultiple('Member', False))

    def __init__(self, *a, **k):
        forms.ModelForm.__init__(self, *a, **k)
        self.fields['primary_member'].queryset = self.instance.recipients
        if self.instance.pk is None:
            self.fields['subscription_members'].queryset = MemberDao.members_for_create_subscription()
        elif self.instance.state == 'waiting':
            self.fields['subscription_members'].queryset = MemberDao.members_for_future_subscription(
                self.instance)
        elif self.instance.state == 'inactive':
            self.fields['subscription_members'].queryset = MemberDao.all_members()
        else:
            self.fields['subscription_members'].queryset = MemberDao.members_for_subscription(
                self.instance)
        self.fields['subscription_members'].initial = self.instance.recipients_all

    def clean(self):
        # enforce integrity constraint on primary_member
        members = self.cleaned_data['subscription_members']
        primary = self.cleaned_data.get('primary_member')
        if primary not in members:
            self.cleaned_data['primary_member'] = members[0] if members else None
        new_members = set(self.cleaned_data['subscription_members'])
        self.instance._future_members = new_members
        return forms.ModelForm.clean(self)

    def save(self, commit=True):
        # HACK: set commit=True, ignoring what the admin tells us.
        # This causes save_m2m to be called.
        return forms.ModelForm.save(self, commit=True)

    def save_m2m(self):
        # update Subscription-Member many-to-one through foreign keys on Members
        if self.instance.state == 'waiting':
            old_members = set(self.instance.members_future.all())
        elif self.instance.state == 'inactive':
            old_members = set(self.instance.members_old.all())
        else:
            old_members = set(self.instance.members.all())
        new_members = set(self.cleaned_data['subscription_members'])
        for obj in old_members - new_members:
            if self.instance.state == 'waiting':
                obj.future_subscription = None
            elif self.instance.state == 'inactive':
                obj.old_subscriptions.remove(self.instance)
            else:
                obj.subscription = None
            obj.save()
        for obj in new_members - old_members:
            if self.instance.state == 'waiting':
                obj.future_subscription = self.instance
            elif self.instance.state == 'inactive':
                obj.old_subscriptions.add(self.instance)
            else:
                obj.subscription = self.instance
            obj.save()
