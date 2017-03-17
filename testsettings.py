# test_settings.py
import os

DEBUG = True

SECRET_KEY = 'fake-key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'juntagrico',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  'yourdatabasename.db',
    }
}

ROOT_URLCONF = 'juntagrico.urls'

AUTHENTICATION_BACKENDS = (
    'juntagrico.helpers.AuthenticateWithEmail',
    'django.contrib.auth.backends.ModelBackend'
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

LANGUAGE_CODE = 'de_CH'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

DATE_INPUT_FORMATS =['%d.%m.%Y',]

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

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
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'juntagrico.personalisation.loaders.personal_directories.Loader'
            ],
            'debug' : True
        },
    },
]

WHITELIST_EMAILS=[]

GOOGLE_API_KEY = 'AIzaSyCcii4Z71qyky54kEQtRhFbB_z-2zbSU28'

