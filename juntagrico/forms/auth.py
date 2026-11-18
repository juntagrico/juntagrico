from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext as _


class JuntagricoPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", _("Passwort ändern")))
