# test_settings.py

DEBUG = True

SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'juntagrico'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  'yourdatabasename.db',
    }
}