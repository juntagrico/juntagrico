from django import forms

from juntagrico.dao.memberdao import MemberDao
from juntagrico.entity.subs import Subscription


# This form exists to restrict primary user choice to users that have actually set the
# current subscription as their subscription


class SubscriptionAdminForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = '__all__'

    def __init__(self, *a, **k):
        forms.ModelForm.__init__(self, *a, **k)
        if 'primary_member' in self.fields.keys():
            self.fields['primary_member'].queryset = MemberDao.members_in_subscription(self.instance)
