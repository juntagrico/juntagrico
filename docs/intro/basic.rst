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
Follow these steps to define admin permissions:

1. Login with the super admin user.
2. Open the data management ("Datenverwaltung") -> Groups -> Add to create a new group.
3. Set a name for the group, e.g. "share management".
4. Select the permission that you want to give to this group:
   Note that the permissions are named in the language of your instance and use your terminology.
   There are 4 basic permissions for each entity: View, Add, Change, Delete.
   Note that also the permissions for related entities need to be given, e.g. as shares are linked to a member
   those who can edit shares also need at least the "view" permission for "members".
   There are additional permissions, e.g. to get email notifications on certain actions.
   Read about these :ref:`special permissions <reference-permissions>` and set them accordingly.
5. Open the data management ("Datenverwaltung") -> User ("Benutzer") and edit the user of the member you want to give the permissions to.
6. If the user needs access to the data management, tick coworker access ("Mitarbeiter-Status").
7. Add the relevant groups for this user and save the user. When you now update the permissions of the group, this users permissions are also updated.

.. note::
    When impersonating the user, e.g. to try their access rights, by default the data management is excluded from impersonation.
    If you want to check their permissions there as well, set the ``IMPERSONATE_URI_EXCLUSIONS`` setting to an empty list. `Read more <https://code.netlandish.com/~petersanchez/django-impersonate/#settings>`_.

Configure Admin Notifications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Email notifications for admins are configured using permissions. See above.


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
