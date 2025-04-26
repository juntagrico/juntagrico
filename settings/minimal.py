from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Core Settings

ALLOWED_HOSTS = ['localhost']

SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'juntagrico.admin_sites.JuntagricoAdminConfig',
    'fontawesomefree',
    'impersonate',
    'juntagrico',
    'crispy_forms',
    'adminsortable2',
    'polymorphic',
    'import_export',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dev.340.db',
    }
}

ROOT_URLCONF = 'urls.dev'

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'juntagrico.context_processors.vocabulary',
            ],
        },
    },
]

LOCALE_PATHS = (
    BASE_DIR / 'juntagrico/locale',
)

# Auth Settings

AUTHENTICATION_BACKENDS = (
    'juntagrico.util.auth.AuthenticateWithEmail',
    'django.contrib.auth.backends.ModelBackend'
)

# Sites Settings

SITE_ID = 1

# Static Files Settings

STATIC_ROOT = BASE_DIR / 'static'
STATIC_URL = '/static/'

# Crispy Forms Settings

CRISPY_TEMPLATE_PACK = 'bootstrap4'
