Settings
========

You can use the following settings to configure juntagrico

Contact Information
-------------------

ORGANISATION_NAME
^^^^^^^^^^^^^^^^^
  The short name of your organisation

  Type: String

  default value

  .. code-block:: python

    "Juntagrico"

ORGANISATION_NAME_CONFIG
^^^^^^^^^^^^^^^^^^^^^^^^
  Additional information to enrich the organisation name with the type of the organisation and its corresponding article

  Type: Dictionary

  default value

  .. code-block:: python

    {"type" : "",
        "gender" : ""}

ORGANISATION_LONG_NAME
^^^^^^^^^^^^^^^^^^^^^^
  The long version of your organisation, if you have one otherwise also use the short one
  
  Type: String

  default value

  .. code-block:: python

    "Juntagrico the best thing in the world"

ORGANISATION_ADDRESS
^^^^^^^^^^^^^^^^^^^^
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
^^^^^^^^^^^^^^^^^^
  The phone number for your organisation

  Type: string

  default value

  .. code-block:: python

    ""

.. _reference-settings-organisation-website:

ORGANISATION_WEBSITE
^^^^^^^^^^^^^^^^^^^^
  The website of your organisation (not the one where you run juntagrico)

  default value

  .. code-block:: python

        {
            'name': "www.juntagrico.juntagrico",
            'url': "https://www.juntagrico.juntagrico"
        }


.. _reference-settings-info-email:

INFO_EMAIL
^^^^^^^^^^
  .. warning::
    Deprecated since version 1.6.0. Use :ref:`CONTACTS <reference-settings-contacts>` instead.

  The general email of your organisation

  Type: String

  default value

  .. code-block:: python

    "info@juntagrico.juntagrico"


.. _reference-settings-contacts:

CONTACTS
^^^^^^^^

  Specifies the email addresses at which members can contact your organisation.

  The setting takes a dictionary of key email pairs, where each key represents the topic for which the email is shown.
  e.g. the email address in ``'for_members'`` is used in places that regard the membership.
  For keys without a specified email address, the ``'general'`` email address is shown.

  example value

  .. code-block:: python

        {
            'general': "info@juntagrico.juntagrico",
            'for_members': "member@juntagrico.juntagrico",
            'for_subscriptions': "subscription@juntagrico.juntagrico",
            'for_shares': "share@juntagrico.juntagrico",
            'technical': "it@juntagrico.juntagrico",
        }

  default value

  .. code-block:: python

        {
            'general': "info@juntagrico.juntagrico",
        }


SERVER_URL
^^^^^^^^^^

  .. warning::
    Deprecated since version 1.6.0. Use :ref:`ORGANISATION_WEBSITE <reference-settings-organisation-website>` instead.

  The base url of your organisation (not the one where you run juntagrico)

  Type: String

  "www.juntagrico.juntagrico"


URL_PROTOCOL
^^^^^^^^^^^^
  The protocol used for urls written in emails and exports.

  default value

  .. code-block:: python

    "https://"

Accounting
----------

ORGANISATION_BANK_CONNECTION
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
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

CURRENCY
^^^^^^^^
  The default currency used within the system

  Type: String

  default value

  .. code-block:: python

    "CHF"


External Documents
------------------

BUSINESS_REGULATIONS
^^^^^^^^^^^^^^^^^^^^
  URL to your business regulations document. The link will be displayed in the signup form and in the welcome mail after a successful registration.
  
  Type: String

  default value

  .. code-block:: python

    ""

BYLAWS
^^^^^^
  URL to your bylaws document. The link will be displayed in the signup form and in the welcome mail after a successful registration.
 
  Type: String

  default value

  .. code-block:: python

    ""

FAQ_DOC
^^^^^^^
  URL to your FAQ document. The link will be displayed in the welcome mail after a successful registration.

  Type: String

  default value

  .. code-block:: python

    ""

EXTRA_SUB_INFO
^^^^^^^^^^^^^^
  If you use extra subscriptions this describes the URL to the document describing them

  Type: String

  default value

  .. code-block:: python

    ""

ACTIVITY_AREA_INFO
^^^^^^^^^^^^^^^^^^
  URL to your document describing your activity areas

  Type: String

  default value

  .. code-block:: python

    ""


Business Year
-------------

BUSINESS_YEAR_START
^^^^^^^^^^^^^^^^^^^
  Defining the start of the business year

  Type: dict with the keys

  - day
  - month

  default value

  .. code-block:: python

    {"day":1, "month":1}


BUSINESS_YEAR_CANCELATION_MONTH
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  The date until you can cancel your subscriptions

  Type: Integer

  default value

  .. code-block:: python

    12


Sign-up
-------

ENABLE_REGISTRATION
^^^^^^^^^^^^^^^^^^^
  Decides if new members can sign up

  Type: Boolean

  default value

  .. code-block:: python

    True

ENABLE_EXTERNAL_SIGNUP
^^^^^^^^^^^^^^^^^^^
  Activates the external signup API and exposes internal depot and subscription info as json.

  Usage: curl -k -L -b -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d 'first_name=John&family_name=Doe&street=Bahnhofstrasse&house_number=42&postal_code=8001&city=Z%C3%BCrich&phone=078%2012345678&email=john.doe@invalid.com&comment=Ich%20freue%20mich%20auf%20den%20Start!&by_laws_accepted=TRUE&subscription_1=1&subscription_2=2&depot_id=1&start_date=2025-12-01&shares=4' 'http://example.com/signup/external'

  Will redirect to signup summary page for final confirmation or redirect to correction of main member details (if mail address exists), subscription selection (on missing main subscription) or number of shares (if requirements not met).

  Type: Boolean

  default value

  .. code-block:: python

    False

SIGNUP_MANAGER
^^^^^^^^^^^^^^

  Overrides the sign-up manager class.
  Change this to modify the sign-up process or when an addon instructs to do so.

  Type: String

  default value

  .. code-block:: python

    "juntagrico.util.sessions.SignupManager"

ENFORCE_MAIL_CONFIRMATION
^^^^^^^^^^^^^^^^^^^
  At login, check if mail address was confirmed. If not, prevent login but show error with instruction and send mail with confirmation link.

  Type: Boolean

  default value

  .. code-block:: python

    True

Membership
----------

BASE_FEE
^^^^^^^^
  Yearly fee for members without a subscription

  Type: String

  default value

  .. code-block:: python

    ""

MEMBERSHIP_END_MONTH
^^^^^^^^^^^^^^^^^^^^
  The month at which end the members can leave the organisation

  Type: Integer

  default value

  .. code-block:: python

    6

MEMBERSHIP_END_NOTICE_PERIOD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  The notice period in months a member needs to account for when cancelling the membership

  Type: Integer

  default value

  .. code-block:: python

    0

Shares
------

ENABLE_SHARES
^^^^^^^^^^^^^
  Enable all share related funtionality

  Type: String

  default value

  .. code-block:: python

    True

REQUIRED_SHARES
^^^^^^^^^^^^^^^
  .. note::
    Added in version 1.7.0.

  Specifies the minimum amount of shares that the main member must order during registration
  regardless of the subscription requirements.

  Type: Integer

  default value

  .. code-block:: python

    1

SHARE_PRICE
^^^^^^^^^^^
  Price of one share

  Type: String

  default value

  .. code-block:: python

    "250"


Jobs
----

ASSIGNMENT_UNIT
^^^^^^^^^^^^^^^
  The mode how assignments are counted: Valid values are EMTITY and HOURS. ENTITY the assignments are counted by occurrence, Hours the value of the assignments are counted by the actual time the user spent on a job.

  Type: String

  default value

  .. code-block:: python

    "ENTITY"

ALLOW_JOB_UNSUBSCRIBE
^^^^^^^^^^^^^^^^^^^^^
  If set to true, members can unsubscribe themselves (or reduce the slots they reserved)
  from a job they signed up to previously by filling out a form.

  Job contacts will be notified.

  If the value is a string, unsubscribing will be allowed and the string will be displayed to the member, when they
  try to unsubscribe from a job.

  Type: Boolean or String

  default value

  .. code-block:: python

    False


PROMOTED_JOB_TYPES
^^^^^^^^^^^^^^^^^^
  Types of jobs which should apear on start page

  Type: List of Strings

  default value

  .. code-block:: python

    []

PROMOTED_JOBS_AMOUNT
^^^^^^^^^^^^^^^^^^^^
  Amount of jobs which should be promoted on the start page

  Type: Integer

  default value

  .. code-block:: python

    2


.. _settings-depot:

Depot
-----

.. _settings-depot-list-generation-days:

DEPOT_LIST_GENERATION_DAYS
^^^^^^^^^^^^^^^^^^^^^^^^^^
  Days on which the delivery list can be generated

  Type: List of Integers representing days of the week, where Monday is 0 and Sunday is 6.

  default value

  .. code-block:: python

    [0,1,2,3,4,5,6]


.. _settings-default-depotlist-generators:

DEFAULT_DEPOTLIST_GENERATORS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  Generators used to generate the depot list. Generators need the method signature ``generator_name(*args, **options)``

  Type: List of Strings which define the different generators to be invoked

  default value

  .. code-block:: python

    ['juntagrico.util.depot_list.default_depot_list_generation']


Appearance
----------

VOCABULARY
^^^^^^^^^^
  Vocabulary dictionary for organisation specific words. _pl indicates the plural of a word. the member key describes the custom name you give your members. the member_type key describes what you call your member in accordance to your oganisation form.

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
        'depot_pl' : 'Depots',
        'package': 'Tasche',
    }


.. _settings-sub-overview-format:

SUB_OVERVIEW_FORMAT
^^^^^^^^^^^^^^^^^^^
  Templates and delimiter for formatting the subscription overview.

  default value

  .. code-block:: python

    {'delimiter': '|',
     'format': '{product}:{size}:{type}={amount}',
     'part_format': '{size}'
    }

STYLES
^^^^^^
  Define styles to be included on all pages. The setting takes a dictionary with two keys:

  - ``static``: A list of css files to be included. These are included using the ``static`` template tag, i.e. the path to the css files must be given, omitting the ``{app}/static/`` part.
  - ``template``: The path to a template file that will be included in the ``<head>`` section on all pages. This can be used to create dynamic css.

  If both keys are defined the template is included before the static css files.

  default value

  .. code-block:: python

    {
        'template': '',
        'static': []
    }

SCRIPTS
^^^^^^^
  Define scripts to be included on all pages.
  If the template key is set, the specified template will be loaded in the scripts part of the page.
  In the static key a list of javascript files can be defined to be included.
  If both keys are defined the template is included before the static javascript files.

  default value

  .. code-block:: python

    {
        'template': '',
        'static': []
    }

FAVICON
^^^^^^^
  If you want to use a custom favicon this specifies the path for your favicon

  Type: String

  default value

  .. code-block:: python

    "/static/juntagrico/img/favicon.ico"

IMAGES
^^^^^^
  Defining the different images for core and job assignments etc

  default value

  .. code-block:: python

    {'status_100': '/static/juntagrico/img/status_100.png',
        'status_75': '/static/juntagrico/img/status_75.png',
        'status_50': '/static/juntagrico/img/status_50.png',
        'status_25': '/static/juntagrico/img/status_25.png',
        'status_0': '/static/juntagrico/img/status_0.png',
        'single_full': '/static/juntagrico/img/single_full.png',
        'single_empty': '/static/juntagrico/img/single_empty.png',
        'single_core': '/static/juntagrico/img/single_core.png',
        'core': '/static/juntagrico/img/core.png'}

BOOTSTRAP
^^^^^^^^^
  If you want to use a customized version of bootstrap this specifies the corresponding path for it

  Type: String

  default value

  .. code-block:: python

    "/static/juntagrico/external/bootstrap/css/bootstrap.min.css"


Email
-----

EMAILS
^^^^^^
  .. warning::
    Deprecated since version 1.6.0. :ref:`Override template directly instead <reference-templates>`.

  Defining the different email templates

  default value

  .. code-block:: python

    {
        'welcome': 'mails/member/member_welcome.txt',
        'co_welcome': 'mails/member/co_member_welcome.txt',
        'co_added': 'mails/member/co_member_added.txt',
        'password': 'mails/member/password_reset.txt',
        'confirm': 'mails/member/email_confirm.txt',
        'j_reminder': 'mails/member/job_reminder.txt',
        'j_canceled': 'mails/member/job_canceled.txt',
        'j_changed': 'mails/member/job_time_changed.txt',
        'j_signup': 'mails/member/job_signup.txt',
        'd_changed': 'mails/member/depot_changed.txt',
        's_created': 'mails/member/share_created.txt',
        'm_left_subscription': 'mails/member/co_member_left_subscription.txt',
        'n_sub': 'mails/admin/subscription_created.txt',
        's_canceled': 'mails/admin/subscription_canceled.txt',
        'a_share_created': 'mails/admin/share_created.txt',
        'a_share_canceled': 'mails/admin/share_canceled.txt',
        'a_subpart_created': 'mails/admin/subpart_created.txt',
        'a_subpart_canceled': 'mails/admin/subpart_canceled.txt',
        'a_member_created': 'mails/admin/member_created.txt',
        'a_depot_list_generated': 'mails/admin/depot_list_generated.txt',
        'm_canceled': 'mails/admin/member_canceled.txt',
    }

MAIL_TEMPLATE
^^^^^^^^^^^^^
  Path to your custom html email template if you want to overwrite the look and feel of the html emails

  Type: String

  default value

  .. code-block:: python

    "mails/email.html"

DEFAULT_MAILER
^^^^^^^^^^^^^^
  The code to send mails. for more info see the code specified in the default value
  The setting ``'juntagrico.util.mailer.batch.Mailer'`` uses a built in batch mailer,
  that sends the emails to the "bcc" recipients in separate emails.
  See ``BATCH_MAILER`` to configure it.

  default value

  .. code-block:: python

    'juntagrico.util.mailer.default.Mailer'


BATCH_MAILER
^^^^^^^^^^^^^^
  Configuration for the batch mailer. These are only effective, if
  DEFAULT_MAILER is set to ``'juntagrico.util.mailer.batch.Mailer'``.
  ``batch_size`` is the number of emails, that is sent in one batch.
  When set to 1, all emails are sent using "to" instead of "bcc".
  ``wait_time`` is the interval in which the batches are sent.

  default value

  .. code-block:: python

    {
        'batch_size': 39,
        'wait_time': 65
    }


FROM_FILTER
^^^^^^^^^^^
  Allows overriding the "from" field of outgoing emails. This can be used to prevent sending emails with a sender of different domain than the SMTP server, which triggers most spam filters.
  The setting consists of a regular expression (``filter_expression``) and a default replacement (``replacement_from``). If the regular expression does NOT match, the default replacement is used as "from", and the original "from" is set as "reply to".

  default value

  .. code-block:: python

    {
        'filter_expression': '.*',
        'replacement_from': ''
    }

WHITELIST_EMAILS
^^^^^^^^^^^^^^^^
  List of regular expression to determine which email addresses should receive emails while DEBUG mode is enabled

  default value

  .. code-block:: python

    []


MAILER_RICHTEXT_OPTIONS
^^^^^^^^^^^^^^^^^^^^^^^
  Configuration overrides of the tinyMCE editor of the mailer view.
  See default config in ``static/juntagrico/js/initMailer.js``.

  default value:

  .. code-block:: python

    {}

Notifications
-------------

ENABLE_NOTIFICATIONS
^^^^^^^^^^^^^^^^^^^^
  List of strings, of notifications that should be enabled:

  -  `'job_subscribed'`: Send an email to the job admin, if a member signs up to a job without leaving a message.

  example:

  .. code-block:: python

    ENABLE_NOTIFICATIONS = ['job_subscribed']

  default value:

  .. code-block:: python

    []


DISABLE_NOTIFICATIONS
^^^^^^^^^^^^^^^^^^^^^

  List of strings, of notifications that should be disabled:

  - `'job_subscription_changed'`: Don't send an email to the job admin if a member changes their job signup without leaving a message.
  - `'job_unsubscribed'`: Don't send an email to the job admin if a member unsubscribes from a job without leaving a message.

  .. note::
    Notifications are always sent, when the member leaves a message, because the message is not stored outside of the email.

  default value:

  .. code-block:: python

    []

GDPR
----

GDPR_INFO
^^^^^^^^^
  URL to your gdpr document

  Type: String

  default value

  .. code-block:: python

    ""

COOKIE_CONSENT
^^^^^^^^^^^^^^
  The text, confirm text, link text and url of the cookie consent

  default value

  .. code-block:: python

    {'text': _('{} verwendet folgende Cookies: session, csfr, cookieconsent.').format(Site.objects.get_current().name),
     'confirm_text': _('einverstanden'),
     'link_text': _('Hier findest du mehr zum Thema'),
     'url': '/my/cookies'
    }

Demo Settings
-------------

DEMO_USER
^^^^^^^^^
  If you run a demo setup and want to display the login name on the login page
  
  Type: String

  default value

  .. code-block:: python

    ''

DEMO_PWD
^^^^^^^^
  If you run a demo setup and want to display the password on the login page

  default value

  .. code-block:: python

    ''
