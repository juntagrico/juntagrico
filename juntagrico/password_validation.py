from django.contrib.auth.password_validation import get_password_validators, UserAttributeSimilarityValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class StaffOnlyPasswordValidator:
    def __init__(self, validators):
        self.validators = get_password_validators(validators)

    def filter(self, user):
        return user.is_staff or user.is_superuser

    def validate(self, password, user=None):
        if user is None or not self.filter(user):
            return

        errors = []
        for validator in self.validators:
            try:
                validator.validate(password, user)
            except ValidationError as error:
                errors.extend(error.error_list)

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _('Für dein Konto ist ein sicheres Passwort pflicht.')


class PermittedOnlyPasswordValidator(StaffOnlyPasswordValidator):
    def filter(self, user):
        return super().filter(user) or user.permissions.exists() or user.groups.exists()


class PrivilegedOnlyPasswordValidator(PermittedOnlyPasswordValidator):
    def filter(self, user):
        return (
            super().filter(user)
            or user.member.coordinated_areas.exists()
            or user.member.coordinated_depots.exists()
        )


class GroupOnlyPasswordValidator(StaffOnlyPasswordValidator):
    GROUP_NAME = 'NeedsStrongPassword'

    def __init__(self, validators, group_name=GROUP_NAME):
        super().__init__(validators)
        self.group_name = group_name

    def filter(self, user):
        return user.groups.filter(self.group_name).exists()


class AccountAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    DEFAULT_USER_ATTRIBUTES = (
        'member__first_name',
        'member__last_name',
        'member__email',
        'member__addr_street',
        'member__addr_zipcode',
        'member__addr_location',
        'member__phone',
        'member__mobile_phone',
        'member__birthday',
    )

    def __init__(
        self,
        user_attributes=DEFAULT_USER_ATTRIBUTES,
        max_similarity=0.7,
    ):
        super().__init__(
            user_attributes=user_attributes,
            max_similarity=max_similarity,
        )
