# Django settings for ortoloco project.
import os
import dj_database_url

DEBUG = os.environ.get("ORTOLOCO_DEBUG", "True") == "True"

WHITELIST_EMAILS = []

def whitelist_email_from_env(var_env_name):
    email = os.environ.get(var_env_name)
    if email:
        WHITELIST_EMAILS.append(email.replace('@gmail.com', '(\+\S+)?@gmail.com'))

whitelist_email_from_env("ORTOLOCO_EMAIL_USER")

if DEBUG is True:
    for key in os.environ.keys():
        if key.startswith("ORTOLOCO_EMAIL_WHITELISTED"):
            whitelist_email_from_env(key)


ADMINS = (
    ('Oli', 'oliver.ganz@gmail.com'),
)
SERVER_EMAIL="server@ortoloco.ch"

# let the users login with their emails
AUTHENTICATION_BACKENDS = (
    'my_ortoloco.helpers.AuthenticateWithEmail',
    'django.contrib.auth.backends.ModelBackend'
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('ORTOLOCO_DATABASE_ENGINE'), # 'django.db.backends.postgresql_psycopg2', #'django.db.backends.sqlite3', # Add , 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.environ.get('ORTOLOCO_DATABASE_NAME'), #''ortoloco', # 'db.sqlite',                      # Or path to database file if using sqlite3.
        'USER': os.environ.get('ORTOLOCO_DATABASE_USER'), #''ortoloco', # The following settings are not used with sqlite3:
        'PASSWORD': os.environ.get('ORTOLOCO_DATABASE_PASSWORD'), #''ortoloco',
        'HOST': os.environ.get('ORTOLOCO_DATABASE_HOST'), #'localhost', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': os.environ.get('ORTOLOCO_DATABASE_PORT', False), #''', # Set to empty string for default.
    }
}

EMAIL_HOST = os.environ.get('ORTOLOCO_EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('ORTOLOCO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('ORTOLOCO_EMAIL_PASSWORD')
EMAIL_PORT = os.environ.get('ORTOLOCO_EMAIL_PORT', 587)
EMAIL_USE_TLS = os.environ.get('ORTOLOCO_EMAIL_TLS', True)

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.orto.xiala.net', '.ortoloco.ch']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de_CH'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
#MEDIA_ROOT = os.path.join(BASE_DIR, 'static/medias/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
# MEDIA_URL = '/medias/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = ( os.path.join(BASE_DIR, 'static'),)


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

#tinyMCE
TINYMCE_JS_URL = '/static/js/tinymce/tinymce.min.js'

TINYMCE_DEFAULT_CONFIG = {
    'theme': "modern",
    'plugins': 'link',
    'relative_urls': False,
    'valid_styles': {
        '*': 'color,text-align,font-size,font-weight,font-style,text-decoration'
    },
    'menu': {
        'edit': {
            'title': 'Edit',
            'items': 'undo redo | cut copy paste | selectall'
        },
        'insert': {
            'title': 'Insert',
            'items': 'link'
        },
        'format': {
            'title': 'Format',
            'items': 'bold italic underline strikethrough superscript subscript | formats | removeformat'
        }
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd3w=vyfqpqmcj#&ge1d0$ch#ff7$qt#6z)lzqt=9pg8wg%d^%s'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'ortoloco/templates'
        ],
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
                'django.template.loaders.app_directories.Loader'
            ],
            'debug' : True
        },
    },
]

IMPERSONATE_REDIRECT_URL = "/my/profil"

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'subdomains.middleware.SubdomainURLRoutingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'impersonate.middleware.ImpersonateMiddleware'
)



# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ortoloco.wsgi.application'



INSTALLED_APPS = (
    'my_ortoloco',
    'static_ortoloco',
    'photologue',
    #'south',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'tinymce',
    'impersonate',
    'storages'
)

# logging config - copied from here: http://stackoverflow.com/questions/18920428/django-logging-on-heroku
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'INFO',
            'class': 'logging.NullHandler',
            },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

PHOTOLOGUE_GALLERY_SAMPLE_SIZE = 3

DEFAULT_FILE_STORAGE = 'ortoloco.utils.MediaS3BotoStorage'

try:
    AWS_ACCESS_KEY_ID = os.environ['ORTOLOCO_AWS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['ORTOLOCO_AWS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['ORTOLOCO_AWS_BUCKET_NAME']
except KeyError:
    raise KeyError('Need to define AWS environment variables: ' +
                   'AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_STORAGE_BUCKET_NAME')

# Default Django Storage API behavior - don't overwrite files with same name
AWS_S3_FILE_OVERWRITE = False

MEDIA_ROOT = 'media'

MEDIA_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'


ROOT_URLCONF = 'ortoloco.urls'

# A dictionary of urlconf module paths, keyed by their subdomain.
SUBDOMAIN_URLCONFS = {
    None: 'ortoloco.urls', 
    'www': 'ortoloco.urls',
    'my': 'ortoloco.myurlsredirect',
}

