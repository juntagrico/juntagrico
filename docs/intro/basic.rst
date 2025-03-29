.. _intro-basic-setup:

Basic Setup
===========

Recommended Settings
--------------------

These settings, in the ``settings.py`` are ideally set, before the instance is used for production,
as changing these settings likely require manual changes on the production data when done later.

Set the Timezone
^^^^^^^^^^^^^^^^

Define the timezone, where your organisation is based, e.g.:

.. code-block:: python

    USE_TZ = True
    TIME_ZONE = 'Europe/Zurich'

If this is added or changed later, all jobs will be shifted in time and will have to be adjusted.

Count assignments by hour
^^^^^^^^^^^^^^^^^^^^^^^^^

If your organization counts the members assignment per hour instead of per job, use this setting:

.. code-block:: python

    ASSIGNMENT_UNIT = 'HOURS'

If you change this later, the setting will only be applied to all new job signups. If you need to change it, it is recommended to change it on the change of your business year.


Initial Configuration
---------------------

These configurations are done in the django admin interface inside of your instance.


.. _configure-website-name-and-domain:

Configure the Website Name and Domain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The website name and domain are displayed in various places on the website and in some emails.
In the Django-Admin under Websites edit the `example.com` entry
and set the names to your website domain and display name.

Custom Logo & Style
-------------------

.. note::
    Replace ``{app}`` with the name of your app in the following instructions.

1. Adjust the file ``{app}/static/{app}/css/customize.css``:

.. code-block:: css

    .juntagrico_logo {
        background: url(/static/{app}/img/logo.png) center center;  /* note that {app} is omitted before "/static" */
        background-size: contain;
        background-repeat: no-repeat;
        display: inline-block;
        width: 300px;  /* adjust to image with */
        height: 300px;  /* adjust to image height */
    }

2. Add the image file of the logo to ``{app}/static/{app}/img/logo.png`` or as specified in the css above.

Other customizations can be added to the same css file.

Depot list setup
----------------
Initial List Generation
^^^^^^^^^^^^^^^^^^^^^^^
The depot lists are created by the following django management command :ref:`generate_depot_list <reference-generate-depot-list>`. This command can
be called manually or using a cronjob.settings-depot

Make sure to set the :ref:`depot list settings <settings-depot>` according to your needs.


Admin Permission Setup
----------------------

It is recommended to limit the access for each person with an administrative task to only include the relevant access.
This will make the navigation easier for them, as the menus only show what they need.
And it will allow them to do their tasks with more confidence, as the risk of changing things by accident is reduced.

Juntagrico does not assume any specific organisation structure.
Instead permissions can be distributed with a high level of granularity.
Read :ref:`Permissions <reference-permissions>` on how to set permissions.


Configure Admin Notifications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Email notifications for admins are also configured :ref:`using permissions <reference-permission-notifications>`.


Text Adjustments
----------------

Adjust Terminology
^^^^^^^^^^^^^^^^^^

Common terms, e.g. for shares, subscriptions, members can be overridden using the ``VOCABULARY`` setting.
Only set the terms you want to override, e.g.:

.. code-block:: python

    VOCABULARY = {
        'subscription': 'Ernteanteil',
        'subscription_pl': 'Ernteanteile'
    }

Change Texts
^^^^^^^^^^^^

By default the texts in juntagrico, including in automated emails, are formulated rather neutral,
such that they are applicable to most of the basic use cases of juntagrico.
You may want to add additional hints or some personal touch to the texts.

Most texts can be modified using :ref:`custom templates <intro-custom-templates>`.
Some texts, e.g. in forms, can be changed with :ref:`custom code <intro-custom-code>`.

.. note::
    If you make modifications to the code or templates, you may have to adapt these,
    whenever they are updated in juntagrico.
