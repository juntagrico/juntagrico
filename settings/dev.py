import os

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

INSTALLED_APPS.append('djrichtextfield')

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

# TODO: this is now needed to configure to mailer richtext.
#  Provide this in juntagrico.defaults to make it easer to set it up
DJRICHTEXTFIELD_CONFIG = {
    'js': ['juntagrico/external/tinymce/tinymce.min.js'],
    'init_template': 'djrichtextfield/init/tinymce.js',
    'settings': {
        'menubar': False,
        'plugins': 'link  lists',
        'toolbar': 'undo redo | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | bullist numlist | link',
        'language': tinymce_lang(LANGUAGE_CODE)
    },
    'profiles': {
        'juntagrico.mailer': {
            'height': 500,
            'relative_urls': False,
            'remove_script_host': False,
            'valid_styles': {
                '*': 'color,text-align,font-size,font-weight,font-style,text-decoration'
            },
            'menubar': 'edit insert format',
            'menu': {
                'edit': {'title': 'Edit', 'items': 'undo redo | cut copy paste | selectall'},
                'insert': {'title': 'Insert', 'items': 'link'},
                'format': {'title': 'Format', 'items': 'bold italic underline strikethrough superscript subscript | formats | removeformat'}
            },
            'toolbar': 'undo redo | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | bullist numlist | link',
        },
        'juntagrico.admin': {}  # this enabled rich text in admin
    },
}


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
