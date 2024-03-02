# testsettings to test collectstatic
from testsettings import *

DEBUG = False
ALLOWED_HOSTS = ['localhost']

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}
