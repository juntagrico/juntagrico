from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, _unicode_ci_compare
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import EmailSender
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
            '<a class="alert-link" href="mailto:{0}">{0}</a>'.format(Config.contacts('for_members'))
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


class JuntagricoPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        # custom sender
        sender = EmailSender.get_sender_from_email(email_message)
        sender.send()

    def get_users(self, email):
        active_members = Member.objects.active().filter(email__iexact=email)
        return (
            member.user
            for member in active_members
            if member.user.has_usable_password() and _unicode_ci_compare(email, member.email)
        )


class MultiplePermissionsRequiredMixin(PermissionRequiredMixin):
    """
    Check multiple permissions. First layer list elements are combined with logical AND,
    Second level with logical OR, third level with logical AND and so on.
    Example:
    permission=required = [
        "Needs this permission and",
        ["this one or", ["this one and", "this one"], "or this one"],
        "and this one"
    ]
    """
    def has_any_permission(self, permissions):
        if isinstance(permissions, str):
            return self.request.user.has_perms((permissions,))
        return any(self.has_all_permissions(perm) for perm in permissions)

    def has_all_permissions(self, permissions):
        if isinstance(permissions, str):
            return self.request.user.has_perms((permissions,))
        return all(self.has_any_permission(perm) for perm in permissions)

    def has_permission(self):
        perms = self.get_permission_required()
        return self.has_all_permissions(perms)
