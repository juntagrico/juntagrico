from django import forms
from django.contrib.admin import widgets, site

from juntagrico.entity.member import SubscriptionMembership
from juntagrico.lifecycle.submembership import check_sub_membership_consistency_ms


class MemberRawIdWidget(widgets.ForeignKeyRawIdWidget):
    def __init__(self, rel, admin_site, attrs=None, using=None, field=None):
        self.field = field
        super().__init__(rel, admin_site, attrs, using)

    def url_parameters(self):
        res = super().url_parameters()
        res['qs_name'] = self.field.queryset.get_property('name')
        res['sub_id'] = self.field.queryset.get_property('subscription_id')
        return res


class SubscriptionMembershipAdminForm(forms.ModelForm):
    class Meta:
        model = SubscriptionMembership
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'member' in self.fields:
            self.fields['member'].widget = MemberRawIdWidget(rel=SubscriptionMembership._meta.get_field('member').remote_field,
                                                             admin_site=site, field=self.fields['member'])

    def clean(self):
        if 'member' in self.cleaned_data:
            check_sub_membership_consistency_ms(self.cleaned_data['member'], self.cleaned_data['subscription'], self.cleaned_data['join_date'])
        return forms.ModelForm.clean(self)
