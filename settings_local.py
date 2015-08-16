import os
from ortoloco.settings import *

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