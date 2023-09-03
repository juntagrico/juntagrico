Management Commands
===================

These commands can be called from a CLI.
Read the `official documentation <https://docs.djangoproject.com/en/4.2/ref/django-admin/>`_ for help.

create_member_for_superusers
----------------------------

The django command ``createsuperuser`` will create a super user. However to be able to login juntagrico requires,
that the user has a member. The command ``create_member_for_superusers`` will create such a member for all existing super users.

Arguments: None


.. _reference-generate-depot-list:

generate_depot_list
-------------------

This command generates all depot lists. This can be used to generate the lists regularly, e.g., using a cronjob.

Arguments:

.. note::
    When using a :ref:`custom depot list generator <settings-default-depotlist-generators>`, the arguments have the effect, that you implement.

.. warning::
    Currently all pending depot changes are applied, when executing the command on a weekday specified in :ref:`DEPOT_LIST_GENERATION_DAYS <settings-depot-list-generation-days>`.
    This behaviour will be DEPRECATED. Use ``--future`` explicitly, to apply the depot changes. Use ``--no-future`` to prevent depot changes in that case.

* ``--force``: If set, the list will be generated even on weekdays that are not specified in the :ref:`DEPOT_LIST_GENERATION_DAYS <settings-depot-list-generation-days>` setting.
* ``--future``: If set, the pending depot changes, i.e. members wanting to change the depot, will be applied, even on on weekdays that are not specified in the :ref:`DEPOT_LIST_GENERATION_DAYS <settings-depot-list-generation-days>` setting.
* ``--no-future``: Prevent applying depot changes, even on weekdays that are specified in the :ref:`DEPOT_LIST_GENERATION_DAYS <settings-depot-list-generation-days>` setting.
* ``--days <number>``:  Specify the reference date, as number of days relative to today. 1 will use tomorrow as reference day, -1 uses yesterday. Default is 0, i.e., today.
  The lists will be generated using all active subscription parts for that reference date, i.e. it can be used to consider future activation dates that are already set.


remind_members
--------------

Sends a job reminder email to all members that are signed up to a job in the next 48 hours.
Will only send the notification once, i.e., executing the command twice will not send another notification to those already notified.

This can be used e.g. with a cronjob.

Arguments: None


mailtexts
---------

Prints the text of all notification emails using real data from the database, but without sending any emails.
This can be used to test, if the emails meet your expectations, e.g. if your modifications work as expected.

.. note::
    As this commands depends on real data, it fails, if no elements are found that meet the criteria, e.g. if there are no co-members.

Arguments: None


generate_testdata
-----------------

.. warning::
    Do not use this command in production

In a testing environment, this command can be used to generate some minimum test data, e.g. subscription types, members, jobs etc.

Arguments: None

generate_testdata_advanced
--------------------------

.. warning::
    Do not use this command in production

Like ``generate_testdata`` but produces a much bigger set of test data using faker (to be installed from the requirements-local.txt).

Arguments: None
