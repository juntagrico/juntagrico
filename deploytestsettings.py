# testsettings to test collectstatic
from testsettings import *

DEBUG = False
ALLOWED_HOSTS = ['localhost']
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
