from django.conf import settings
from django.core.checks import Tags, Warning, register


@register(Tags.compatibility)
def check_deprecated_settings(app_configs, **kwargs):
    errors = []
    if hasattr(settings, 'INFO_EMAIL'):
        errors.append(
            Warning(
                'INFO_EMAIL is deprecated since juntagrico 1.6.0',
                hint='Use CONTACTS instead',
                obj=settings,
                id='juntagrico.deprecation.W001',
            )
        )
    if hasattr(settings, 'SERVER_URL'):
        errors.append(
            Warning(
                'SERVER_URL is deprecated since juntagrico 1.6.0',
                hint='Use ORGANISATION_WEBSITE instead',
                obj=settings,
                id='juntagrico.deprecation.W002',
            )
        )
    return errors
