from .dev import *  # noqa: F401

INSTALLED_APPS = [
    'juntagrico_legacy',
] + INSTALLED_APPS


ROOT_URLCONF = 'urls.legacy'
