Settings
========

You can use the following settings to configure juntagrico


VOCABULARY
-------------
  Vocabulary dictionary for organisation specific words. _pl indicates the plural of a word. the member key describes the custom name you give your members. the member_type key describes what you call your member in acordance to your oganisation form.
  
  Type: Dictionary

  default value

  .. code-block:: python

    {
        'member': 'Mitglied',
        'member_pl' : 'Mitglieder',
        'assignment' : 'Arbeitseinsatz',
        'assignment_pl' : 'Arbeitseinsätze',
        'share' : 'Anteilschein',
        'share_pl' : 'Anteilscheine',
        'subscription' : 'Abo',
        'subscription_pl' : 'Abos',
        'co_member' : 'Mitabonnent',
        'co_member_pl' : 'Mitabonnenten',
        'price' : 'Betriebsbeitrag',
        'member_type' : 'Mitglied',
        'member_type_pl' : 'Mitglieder',
        'depot' : 'Depot',
        'depot_pl' : 'Depots'
    }

ORGANISATION_NAME
-----------------
  The short name of your orgnisation

  Type: String

  default value

  .. code-block:: python

    "Juntagrico"

ORGANISATION_NAME_CONFIG
------------------------
  Additional information to enrich the organisation name with the type of the organisation and its corresponding article

  Type: Dictionary

  default value

  .. code-block:: python

    {"type" : "",
        "gender" : ""}

ORGANISATION_LONG_NAME
----------------------
  The long version of your organisation, if you have one otherwise also use the short one
  
  Type: String

  default value

  .. code-block:: python

    "Juntagrico the best thing in the world"

ORGANISATION_ADDRESS
--------------------
  The address of your organisation
  
  Type: dict with the keys
  - name
  - street
  - number
  - zip
  - city
  - extra

  default value

  .. code-block:: python

    {"name":"Juntagrico", 
        "street" : "Fakestreet",
        "number" : "123",
        "zip" : "12456",
        "city" : "Springfield",
        "extra" : ""}

ORGANISATION_PHONE
------------------
  The phone number for your organisation

  Type: string

  default value

  .. code-block:: python

    ""

ORGANISATION_BANK_CONNECTION
----------------------------
  the bank connection information of your organisation
  
  Type: dict with the keys
  - PC (postkonto)
  - BIC
  - IBAN
  - NAME

  default value

  .. code-block:: python

    {"PC" : "01-123-5",
        "IBAN" : "CH 00 12345 67890 12345 67890 10",
        "BIC" : "BIC12345XX",
        "NAME" : "Juntagrico Bank",}

INFO_EMAIL
----------
  The general email of your organisation
  
  Type: String

  default value

  .. code-block:: python

    "info@juntagrico.juntagrico"

SERVER_URL
----------
  The base url of your organisation (not the one where you run juntagrico)

  Type: String  

  default value

  .. code-block:: python

    "www.juntagrico.juntagrico"

ADMINPORTAL_NAME
----------------
  The name you want to use for the portal
  
  Type: String

  default value

  .. code-block:: python

    "my.juntagrico"

ADMINPORTAL_SERVER_URL
----------------------
  The base URL where you run juntagrico (and where your static lies)
  
  Type: String

  default value

  .. code-block:: python

    "my.juntagrico.juntagrico"

BUSINESS_REGULATIONS
--------------------
  URL to your business regulations document
  
  Type: String

  default value

  .. code-block:: python

    ""

BYLAWS
------
  URL to your bylaws document
  
  Type: String

  default value

  .. code-block:: python

    ""

GDPR_INFO
------
  URL to your gdpr document

  Type: String

  default value

  .. code-block:: python

    ""

MAIL_TEMPLATE
-------------
  Path to your custom html email template if you want to overwrite the look and feel of the html emails
  
  Type: String

  default value

  .. code-block:: python

    "mails/email.html"

STYLE_SHEET
-----------
  If you want to use a custom design this specifies the path for your css
  
  Type: String

  default value

  .. code-block:: python

    "/static/css/personal.css"

FAVICON
-------
  If you want to use a custom favicon this specifies the path for your favicon
  
  Type: String

  default value

  .. code-block:: python

    "/static/img/favicon.ico"

FAQ_DOC
-------
  URL to your FAQ document
  
  Type: String

  default value

  .. code-block:: python

    ""

BOOTSTRAP
---------
  If you want to use a customized version of bootstrap this specifies the corresponding path for it
  
  Type: String

  default value

  .. code-block:: python

    "/static/external/bootstrap-3.3.1/css/bootstrap.min.css"

EXTRA_SUB_INFO
--------------
  If you use extra subscriptions this describes the URL to the document describing them
  
  Type: String

  default value

  .. code-block:: python

    ""

ACTIVITY_AREA_INFO
------------------
  URL to your document describing your activity areas
  
  Type: String

  default value

  .. code-block:: python

    ""

SHARE_PRICE
-----------
  Price of one share
  
  Type: String

  default value
  
  .. code-block:: python

    "250"


ENABLE_SHARES
-----------
  Enable all share related funtionality

  Type: String

  default value

  .. code-block:: python

    True

ENABLE_REGISTRATION
-----------
  Decides if new member can register

  Type: Boolean

  default value

  .. code-block:: python

    True

BASE_FEE
--------
  Yearly fee for members without a subscription
  
  Type: String

  default value
  
  .. code-block:: python

    ""

CURRENCY
--------
  The default currency used within the system
  
  Type: String

  default value
  
  .. code-block:: python

    "CHF"

ASSIGNMENT_UNIT
---------------
  The mode how assignments are counted: Valid values are EMTITY and HOURS. ENTITY the assignments are counted by occurrence, Hours the value of the assignments are counted by the actual time the user spent on a job.
  
  Type: String

  default value
  
  .. code-block:: python

    "ENTITY"

PROMOTED_JOB_TYPES
------------------
  Types of jobs which should apear on start page
  
  Type: List of Strings

  default value

  .. code-block:: python

    []

PROMOTED_JOBS_AMOUNT
--------------------
  Amount of jobs which should be promoted on the start page
  
  Type: Integer

  default value

  .. code-block:: python

    2

DEPOT_LIST_GENERATION_DAYS
--------------------------
  Days on which the delivery list can be generated
  
  Type: List of Integers representing days of the week, where Monday is 0 and Sunday is 6.

  default value

  .. code-block:: python

    [0,1,2,3,4,5,6]

BUSINESS_YEAR_START
-------------------
  Defining the start of the business year
  
  Type: dict with the keys
  - day
  - month

  default value

  .. code-block:: python

    {"day":1, "month":1}

BUSINESS_YEAR_CANCELATION_MONTH
-------------------------------
  The date until you can cancel your subscriptions
  
  Type: Integer

  default value

  .. code-block:: python

    12

MEMBERSHIP_END_MONTH
--------------------
  The month at which end the members can leave the organisation
  
  Type: Integer

  default value

  .. code-block:: python

    6

DEMO_USER
---------
  If you run a demo setup and want to display the login name on the login page
  
  Type: String

  default value

  .. code-block:: python

    ''

DEMO_PWD
--------
  If you run a demo setup and want to display the password on the login page

  default value

  .. code-block:: python

    ''

DEFAULT_MAILER
--------
  The code to send mails. for more info see the code specified in the default value

  default value

  .. code-block:: python

    'juntagrico.util.defaultmailer.Mailer'


FROM_FILTER
-----------
  Consisting of a regular expression and a default replacement. If the regular expression does not match the default replacement is used, and the orogonal from is set as reply to

  default value

  .. code-block:: python
    {
        'filter_expression': '.*',
        'replacement_from': ''
    }
COOKIE_CONSENT
-----------
  The text, confirm text, link text and url of the cookie consent

  default value

  .. code-block:: python

    {'text': _('{} verwendet folgende Cookies: session, csfr, cookieconsent.').format(Config.adminportal_name()),
     'confirm_text': _('einverstanden'),
     'link_text': _('Hier findest du mehr zum Thema'),
     'url': '/my/cookies'
    }

IMAGES
------
  Defining the different images for core and job assignments etc

  default value

  .. code-block:: python

    {'status_100': '/static/img/status_100.png', 
        'status_75': '/static/img/status_75.png', 
        'status_50': '/static/img/status_50.png', 
        'status_25': '/static/img/status_25.png', 
        'status_0': '/static/img/status_0.png', 
        'single_full': '/static/img/single_full.png', 
        'single_empty': '/static/img/single_empty.png', 
        'single_core': '/static/img/single_core.png',
        'core': '/static/img/core.png'}

EMAILS
------
  Defining the different email templates

  default value

  .. code-block:: python

    {
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
    }
