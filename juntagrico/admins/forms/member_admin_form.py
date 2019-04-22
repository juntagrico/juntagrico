from django import forms
from django.urls import reverse
from django.utils.translation import gettext as _

from juntagrico.entity.member import Member
from juntagrico.util.admin import MyHTMLWidget
from juntagrico.config import Config


class MemberAdminForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = '__all__'

    def __init__(self, *a, **k):
        forms.ModelForm.__init__(self, *a, **k)
        member = k.get('instance')
        link = self.get_subscription_link(member, member.subscription)
        self.fields['subscription_link'].initial = link
        link = self.get_subscription_link(member, member.future_subscription)
        self.fields['future_subscription_link'].initial = link

    @staticmethod
    def get_subscription_link(member, subscription):
        if member is None:
            link = ''
        elif subscription:
            url = reverse('admin:juntagrico_subscription_change',
                          args=(subscription.id,))
            link = '<a href=%s>%s</a>' % (url, subscription)
        else:
            link = _('Kein/e/n {0}').format(Config.vocabulary('subscription'))
        return link

    subscription_link = forms.URLField(widget=MyHTMLWidget(), required=False,
                                       label='Abo')
    future_subscription_link = forms.URLField(widget=MyHTMLWidget(), required=False,
                                              label=_('Zukünftige/r/s {0}').format(Config.vocabulary('subscription')))
