import os

from juntagrico.defaults import richtextfield_config
from .minimal import *  # noqa: F401

from juntagrico.util.settings import tinymce_lang


# Core Settings

DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING' if os.environ.get('GITHUB_WORKFLOW') else 'DEBUG',
    },
}

# enable only to test addon features
# INSTALLED_APPS.insert(9, 'juntagrico_test_addon')


# settings for CI
if os.environ.get('GITHUB_WORKFLOW'):
    if os.environ.get('GITHUB_MYSQL'):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'mysql',
                'USER': 'root',
                'PASSWORD': 'mysql',
                'HOST': '127.0.0.1',
                'PORT': '3306',
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'testdb',
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'HOST': '127.0.0.1',
                'PORT': '5432',
            }
        }

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


class InvalidTemplateVariable(str):
    def __mod__(self, other):
        raise NameError(f"In template, undefined variable or unknown value for: '{other}'")


TEMPLATES[0]['OPTIONS'].update({
    # 'string_if_invalid': InvalidTemplateVariable("%s"),
    'debug': DEBUG,
})


USE_I18N = True
USE_L10N = True  # required to pass tests
LANGUAGE_CODE = 'de-CH'  # required to pass tests
DATE_INPUT_FORMATS = ['%d.%m.%Y', ]

USE_TZ = True  # required to pass tests


# Auth Settings

LOGIN_REDIRECT_URL = "/"


# Impersonate Settings

IMPERSONATE = {
    'REDIRECT_URL': '/my/profile',
}


# Import Export Settings

IMPORT_EXPORT_EXPORT_PERMISSION_CODE = 'view'  # required to pass tests


# Crispy Forms Settings

CRISPY_FAIL_SILENTLY = not DEBUG


# Rich text Settings

DJRICHTEXTFIELD_CONFIG = richtextfield_config(LANGUAGE_CODE, use_in_admin=True)

# Juntagrico Settings

WHITELIST_EMAILS = []


def whitelist_email_from_env(var_env_name):
    email = os.environ.get(var_env_name)
    if email:
        WHITELIST_EMAILS.append(email)


if DEBUG is True:
    for key in os.environ.keys():
        if key.startswith("JUNTAGRICO_EMAIL_WHITELISTED"):
            whitelist_email_from_env(key)


# required to pass tests
CONTACTS = {
    'general': "info@juntagrico.juntagrico",
    'for_members': "member@juntagrico.juntagrico",
    'for_subscriptions': "subscription@juntagrico.juntagrico",
    'for_shares': "share@juntagrico.juntagrico",
    'technical': "it@juntagrico.juntagrico",
}

ENABLE_SHARES = os.environ.get('EXCLUDE_TEST', 'none') != 'shares'  # required to pass tests

BUSINESS_REGULATIONS = 'https://juntagrico.juntagrico/business-regulations'
BYLAWS = 'https://juntagrico.juntagrico/bylaws'
FAQ_DOC = 'https://juntagrico.juntagrico/faq'
EXTRA_SUB_INFO = 'https://juntagrico.juntagrico/sub-info'
ACTIVITY_AREA_INFO = 'https://juntagrico.juntagrico/area-info'
