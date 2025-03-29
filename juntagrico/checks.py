from django.conf import settings
from django.core.checks import Tags, Warning, Error, register
from django.template import engines
from django.template.backends.django import DjangoTemplates


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


@register(Tags.templates)
def check_context_processors(app_configs, **kwargs):
    errors = []
    django_templates_instance = None
    for engine in engines.all():
        if isinstance(engine, DjangoTemplates):
            django_templates_instance = engine.engine
    if not django_templates_instance:
        errors.append(
            Error(
                'A "django.template.backends.django.DjangoTemplates" instance '
                'must be configured in TEMPLATES in order to use juntagrico.',
                obj=settings,
                id='juntagrico.E001',
            )
        )
    elif 'juntagrico.context_processors.vocabulary' not in django_templates_instance.context_processors:
        errors.append(
            Error(
                '"juntagrico.context_processors.vocabulary" must '
                'be enabled in DjangoTemplates (TEMPLATES) in order to use juntagrico.',
                id='juntagrico.E002',
            )
        )
    return errors
