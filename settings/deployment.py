# these settings tests if collectstatic will work during deployment
from .dev import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ['localhost']

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}
