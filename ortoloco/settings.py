# Django settings for ortoloco project.
import os
import dj_database_url

DEBUG = os.environ.get("ORTOLOCO_DEBUG", "True") == "True"

TEMPLATE_DEBUG = DEBUG

WHITELIST_EMAILS = []

def whitelist_email_from_env(var_env_name):
    email = os.environ.get(var_env_name)
    if email:
        WHITELIST_EMAILS.append(email.replace('@gmail.com', '(\+\S+)?@gmail.com'))

whitelist_email_from_env("ORTOLOCO_EMAIL_USER")
whitelist_email_from_env("ORTOLOCO_EMAIL_WHITELISTED_1")
whitelist_email_from_env("ORTOLOCO_EMAIL_WHITELISTED_2")

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
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/tosomeNotWorkingUrl/'

# Additional locations of static files
STATICFILES_DIRS = (
#"/static/",
# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
)


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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

IMPERSONATE_REDIRECT_URL = "/my/profil"

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'impersonate.middleware.ImpersonateMiddleware'
)

ROOT_URLCONF = 'ortoloco.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ortoloco.wsgi.application'

#from photologue import PHOTOLOGUE_TEMPLATE_DIR

TEMPLATE_DIRS = (
    'ortoloco/templates',
    # PHOTOLOGUE_TEMPLATE_DIR
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'my_ortoloco',
    'static_ortoloco',
    'photologue',
    'south',
    'django_cron',
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

GALLERY_SAMPLE_SIZE = 4

#os.environ['S3_USE_SIGV4'] = 'True'

# S3Boto storage settings for photologue example project.

DEFAULT_FILE_STORAGE = 'ortoloco.utils.MediaS3BotoStorage'
#STATICFILES_STORAGE = 'ortoloco.utils.StaticS3BotoStorage'

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

#STATIC_ROOT = '/static/'
#STATIC_URL = 'http://%s.s3.amazonaws.com/static/' % AWS_STORAGE_BUCKET_NAME

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
