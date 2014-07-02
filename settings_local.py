import os
from ortoloco.settings import *

DATABASES = {
    'default': {

        # To use with MySql
        # 'ENGINE': 'django.db.backends.mysql',
        # 'NAME': 'mysql_db_name',

        # To use with sqlite3
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite', # Or path to database file if using sqlite3.

        # To use with oracle
        # 'ENGINE': 'django.db.backends.oracle',
        # 'NAME': 'oracle_db_name',

        # The following settings are not used with sqlite3:
        # 'USER': 'django',
        # 'PASSWORD': 'django',
        #'HOST': 'localhost', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        #'PORT': '',          # Set to empty string for default.
    }
}

STATIC_URL = '/static/tosomeotherurl/'

LOGGING = {
}

# Setting to send emails
# Do not need to be set up if not needed
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = '<your-username>@gmail.com'
EMAIL_HOST_PASSWORD = '<your-password>'
EMAIL_PORT = 587
EMAIL_USE_TLS = True