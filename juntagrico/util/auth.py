from django.contrib.auth.models import User

from juntagrico.models import Member


class AuthenticateWithEmail(object):
    @staticmethod
    def authenticate(username=None, password=None):
        try:
            user = Member.objects.get(**{'email': username}).user
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
