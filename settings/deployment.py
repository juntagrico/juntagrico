# these settings tests if collectstatic will work during deployment
from .dev import *  # noqa: F401

DEBUG = False
ALLOWED_HOSTS = ['localhost']

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}
