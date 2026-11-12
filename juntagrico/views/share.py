from crispy_forms.layout import Layout, Field

from juntagrico.forms import ShareOrderForm
from juntagrico.util.management import create_share


class ShareInvitationForm(ShareOrderForm):
    def __init__(self, required, existing=0, *args, **kwargs):
        super().__init__(required, existing, *args, **kwargs)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Field('of_member', template=self.field_template),
        )

    def save(self, member):
        amount = self.cleaned_data['of_member']
        create_share(member, amount)
        return amount
