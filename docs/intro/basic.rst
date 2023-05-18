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

Configure the Website Name and Domain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The website name and domain are displayed in various places on the website and in some emails.
In the Django-Admin under Websites edit the `example.com` entry
and set the names to your website domain and display name.


Depot list setup
----------------
Initial List Generation
^^^^^^^^^^^^^^^^^^^^^^^
The depot lists are created by the following django management command :command:`generate_depot_list`. This command can
be called manually or using a cronjob.


Email Adjustments
-----------------

TODO

Configure Admin Notifications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO

Text Adjustments
----------------

TODO
