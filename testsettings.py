# test_settings.py
import os

from juntagrico.util.settings import tinymce_lang

DEBUG = True

SECRET_KEY = 'fake-key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMPERSONATE = {
    'REDIRECT_URL': '/my/profile',
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'fontawesomefree',
    'impersonate',
    'juntagrico',
    'crispy_forms',
    'adminsortable2',
    'djrichtextfield',
    'polymorphic',
    'import_export',
    # enable only to test addon stuff
    # 'juntagrico_test_addon',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  'yourdatabasename.db',
    }
}

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

ROOT_URLCONF = 'testurls'

AUTHENTICATION_BACKENDS = (
    'juntagrico.util.auth.AuthenticateWithEmail',
    'django.contrib.auth.backends.ModelBackend'
)

MIDDLEWARE = [

    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
]

EMAIL_HOST = os.environ.get('JUNTAGRICO_EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('JUNTAGRICO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('JUNTAGRICO_EMAIL_PASSWORD')
EMAIL_PORT = os.environ.get('JUNTAGRICO_EMAIL_PORT', 2525)
EMAIL_USE_TLS = os.environ.get('JUNTAGRICO_EMAIL_TLS', False)

WHITELIST_EMAILS = []


def whitelist_email_from_env(var_env_name):
    email = os.environ.get(var_env_name)
    if email:
        WHITELIST_EMAILS.append(email)


if DEBUG is True:
    for key in os.environ.keys():
        if key.startswith("JUNTAGRICO_EMAIL_WHITELISTED"):
            whitelist_email_from_env(key)

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

LANGUAGE_CODE = 'de-CH'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

DATE_INPUT_FORMATS = ['%d.%m.%Y', ]

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


class InvalidTemplateVariable(str):
    def __mod__(self, other):
        raise NameError(f"In template, undefined variable or unknown value for: '{other}'")


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader'
            ],
            # 'string_if_invalid': InvalidTemplateVariable("%s"),
            'debug': True
        },
    },
]

LOGIN_REDIRECT_URL = "/"

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'juntagrico/locale'),
)

CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_FAIL_SILENTLY = not DEBUG

DJRICHTEXTFIELD_CONFIG = {
    'js': ['juntagrico/external/tinymce/tinymce.min.js'],
    'init_template': 'djrichtextfield/init/tinymce.js',
    'settings': {
        'menubar': False,
        'plugins': 'link  lists',
        'toolbar': 'undo redo | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | bullist numlist | link',
        'language': tinymce_lang(LANGUAGE_CODE)
    }
}

CONTACTS = {
    'general': "info@juntagrico.juntagrico",
    'for_members': "member@juntagrico.juntagrico",
    'for_subscriptions': "subscription@juntagrico.juntagrico",
    'for_shares': "share@juntagrico.juntagrico",
    'technical': "it@juntagrico.juntagrico",
}

IMPORT_EXPORT_EXPORT_PERMISSION_CODE = 'view'
