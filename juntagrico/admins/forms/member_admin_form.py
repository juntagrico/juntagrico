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
        if member is None:
            link = ''
        elif member.subscription:
            url = reverse('admin:juntagrico_subscription_change',
                          args=(member.subscription.id,))
            link = '<a href=%s>%s</a>' % (url, member.subscription)
        else:
            link = _('Kein/e/n {0}').format(Config.vocabulary('subscription'))
        self.fields['subscription_link'].initial = link
        if member is None:
            link = ''
        elif member.future_subscription:
            url = reverse('admin:juntagrico_subscription_change',
                          args=(member.future_subscription.id,))
            link = '<a href=%s>%s</a>' % (url, member.future_subscription)
        else:
            link =  _('Kein/e/n {0}').format(Config.vocabulary('subscription'))
        self.fields['future_subscription_link'].initial = link

    subscription_link = forms.URLField(widget=MyHTMLWidget(), required=False,
                                       label='Abo')
    future_subscription_link = forms.URLField(widget=MyHTMLWidget(), required=False,
                                              label= _('Zukünftige/r/s {0}').format(Config.vocabulary('subscription')))
