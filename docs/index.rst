Welcome to the juntagrico documentation
=======================================
Installation
------------

Install juntagrico from it's git repository or using pip. You need an django app.

The following django settings are nescessary to run juntagrico.

Additional to juntagrico the following apps have to installed into django:

.. code-block:: python

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'juntagrico',
        'impersonate',
    ]
    
The following authentication settings are required

.. code-block:: python

    AUTHENTICATION_BACKENDS = (
        'juntagrico.util.auth.AuthenticateWithEmail',
        'django.contrib.auth.backends.ModelBackend'
    )
    
Additionally also some changes in the middleware have to to be added

.. code-block:: python

    MIDDLEWARE = [
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'impersonate.middleware.ImpersonateMiddleware',
    ]
    
Since we use session we need a serializer

.. code-block:: python

    SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
    
Django also needs to be configured to send emails and to access a database. If you need more helping points see the testsettings in the project folder





For your convenience all settings with default values to copy into your settings.py and to adapt them

  .. code-block:: python

    MEMBER_STRING = 'Mitglied'
    MEMBERS_STRING = 'Mitglieder'
    ASSIGNMENT_STRING = 'Arbeitseinsatz'
    ASSIGNMENTS_STRING = 'Arbeitseinsätze'
    ORGANISATION_NAME = 'Juntagrico'
    ORGANISATION_LONG_NAME = 'Juntagrico the best thing in the world'
    ORGANISATION_ADDRESS = {'name':'Juntagrico',
                        'street' : 'Fakestreet',
                        'number' : '123',
                        'zip' : '12456',
                        'city' : 'Springfield',
                        'extra' : ''}
    ORGANISATION_BANK_CONNECTION = {'PC' : '01-123-5', 
                                'IBAN' : 'CH 00 12345 67890 12345 67890 10', 
                                'BIC' : 'BIC12345XX', 
                                'NAME' : 'Juntagrico Bank', 
                                'ESR' : '01-123-45'}
    INFO_EMAIL = 'info@juntagrico.juntagrico'
    SERVER_URL = 'www.juntagrico.juntagrico'
    ADMINPORTAL_NAME = 'my.juntagrico'
    ADMINPORTAL_SERVER_URL = 'my.juntagrico.juntagrico'
    BUSINESS_REGULATIONS = '/static/docs/business_regulations.pdf'
    BYLAWS = '/static/docs/bylaws.pdf'
    MAIL_TEMPLATE = 'mails/email.html'
    STYLE_SHEET = '/static/css/personal.css'
    FAVICON = '/static/img/favicon.ico'
    BOOTSTRAP = '/static/external/bootstrap-3.3.1/css/bootstrap.min.css'
    FAQ_DOC = '/static/doc/fac.pdf'
    EXTRA_SUB_INFO = '/static/doc/extra_sub_info.pdf'
    ACTIVITY_AREA_INFO = '/static/doc/activity_area_info.pdf'
    SHARE_PRICE = '250'
    CURRENCY = 'CHF'
    ASSIGNMENT_UNIT = 'ENTITY'
    PROMOTED_JOB_TYPES = []
    PROMOTED_JOBS_AMOUNT = 2
    DEPOT_LIST_COVER_SHEETS = 'x'
    DEPOT_LIST_OVERVIEWS = 'x'
    DEPOT_LIST_GENERATION_DAYS = [1,2,3,4,5,6,7]	
    BILLING = False
    BUSINESS_YEAR_START = {'day':1, 'month':1}
    BUSINESS_YEAR_CANCELATION_MONTH = 12
    DEMO_USER = ''
    DEMO_PWD = ''
    IMAGES[key] = {'status_100': '/static/img/status_100.png', 
                'status_75': '/static/img/status_75.png', 
                'status_50': '/static/img/status_50.png', 
                'status_25': '/static/img/status_25.png', 
                'status_0': '/static/img/status_0.png', 
                'single_full': '/static/img/single_full.png', 
                'single_empty': '/static/img/single_empty.png', 
                'single_core': '/static/img/single_core.png',
                'core': '/static/img/core.png'}
    GOOGLE_API_KEY = 'GOOGLE_API_KEY'
    EMAILS = {
        'welcome': 'mails/welcome_mail.txt',
        'co_welcome': 'mails/welcome_added_mail.txt',
        'co_added': 'mails/added_mail.txt',
        'password': 'mails/password_reset_mail.txt',
        'j_reminder': 'mails/job_reminder_mail.txt',
        'j_canceled': 'mails/job_canceled_mail.txt',
        'confirm': 'mails/confirm.txt',
        'j_changed': 'mails/job_time_changed_mail.txt',
        'j_signup': 'mails/job_signup_mail.txt',
        'd_changed': 'mails/depot_changed_mail.txt',
        's_created': 'mails/share_created_mail.txt',
        'n_sub': 'mails/new_subscription.txt',
        's_canceled': 'mails/subscription_canceled_mail.txt',
        'm_canceled': 'mails/membership_canceled_mail.txt',
        'b_share': 'mails/bill_share.txt',
        'b_sub': 'mails/bill_sub.txt',
        'b_esub': 'mails/bill_extrasub.txt'
    }
    BASE_FEE = ''
    ORGANISATION_PHONE = ''
    
    
.. toctree::
   :maxdepth: 2
   :numbered:

   settings.rst
   release_notes.rst
