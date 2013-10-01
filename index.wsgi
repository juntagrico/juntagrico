#!/usr/bin/env python

import os
import sys

# redirect sys.stdout to sys.stderr for bad libraries like geopy that uses
# print statements for optional import exceptions.
sys.stdout = sys.stderr

import os
import site

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.abspath(os.path.join(BASE_PATH, '../python-env/ortoloco.ch/'))
activate_this = os.path.abspath(os.path.join(ENV_PATH, 'bin/activate_this.py'))
execfile(activate_this, dict(__file__=activate_this))
#site.addsitedir(join(ENV_PATH, 'lib/python2.7/site-packages'))
#sys.path.insert(0, join(ENV_PATH, 'lib/python2.7'))
if not BASE_PATH in sys.path:
    sys.path.insert(0, BASE_PATH)
APP_PATH = os.path.join(BASE_PATH, 'ortoloco')
if not APP_PATH in sys.path:
    sys.path.insert(0, APP_PATH)
if not '.' in sys.path:
    sys.path.insert(0, '.')

print sys.path
from ortoloco import settings

os.environ["DJANGO_SETTINGS_MODULE"] = "ortoloco.settings"
os.environ["DJANGO_ENV"] = "prod"
os.environ["LC_ALL"] = "en_US.UTF-8"
from django.conf import settings

from django.core.handlers.wsgi import WSGIHandler

application = WSGIHandler()
