from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.models import Member


class AuthenticateWithEmail(object):
    @staticmethod
    def authenticate(request, username=None, password=None):
        try:
            user = Member.objects.get(email__iexact=username).user
            if user.check_password(password):
                return user
        except Member.DoesNotExist:
            return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class JuntagricoAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _('Sorry, das ist kein gültiges Login'),
        'inactive': _('Deine Mitgliedschaft ist deaktiviert. Bei Fragen melde dich bitte bei {}').format(
            '<a class="alert-link" href="mailto:{0}">{0}</a>'.format(Config.info_email())
        ),
    }

    def confirm_login_allowed(self, user):
        if user.member.inactive:
            raise ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )


class JuntagricoLoginView(LoginView):
    form_class = JuntagricoAuthenticationForm
