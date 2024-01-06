Management Commands
===================

These commands can be called from a CLI.
Read the `official documentation <https://docs.djangoproject.com/en/4.2/ref/django-admin/>`_ for help.

Call the commands with ``-h`` for more details on the usage.

create_member_for_superusers
----------------------------

The django command ``createsuperuser`` will create a super user. However to be able to login juntagrico requires,
that the user has a member. The command ``create_member_for_superusers`` will create such a member for all existing super users.

.. _reference-generate-depot-list:

generate_depot_list
-------------------

This command generates all depot lists. This can be used to generate the lists regularly, e.g., using a cronjob.

.. note::
    When using a :ref:`custom depot list generator <settings-default-depotlist-generators>`, the arguments have the effect, that you implement.

.. warning::
    Currently all pending depot changes are applied, when executing the command on a weekday specified in :ref:`DEPOT_LIST_GENERATION_DAYS <settings-depot-list-generation-days>`.
    This behaviour will be DEPRECATED. Use ``--future`` explicitly, to apply the depot changes. Use ``--no-future`` to prevent depot changes in that case.

remind_members
--------------

Sends a job reminder email to all members that are signed up to a job in the next 48 hours.
Will only send the notification once, i.e., executing the command twice will not send another notification to those already notified.

shift_time
----------

When changing the ``TIMEZONE`` setting on an existing installation,
you will have to adapt the times of all existing jobs. This command helps you with that task.

.. warning::
    No notification emails will be sent, when changing the job time with this command.

This command is also available to super users under the hidden url ``/command/shifttime``.

mailtexts
---------

Prints the text of all notification emails using real data from the database, but without sending any emails.
This can be used to test, if the emails meet your expectations, e.g. if your modifications work as expected.

.. note::
    As this commands depends on real data, it fails, if no elements are found that meet the criteria, e.g. if there are no co-members.

generate_testdata
-----------------

.. warning::
    Do not use this command in production

In a testing environment, this command can be used to generate some minimum test data, e.g. subscription types, members, jobs etc.

generate_testdata_advanced
--------------------------

.. warning::
    Do not use this command in production

Like ``generate_testdata`` but produces a much bigger set of test data using faker (to be installed from the requirements-local.txt).
