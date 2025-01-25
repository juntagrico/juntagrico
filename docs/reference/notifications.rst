.. _reference-notifications:

Notifications & Emails
======================

Juntagrico sends out automatic notifications to members and admins via email.

The content of each notification can be modified by overriding their template, listed below.
See :ref:`template overrides <reference-templates>` on how to set it up.

For some notifications recipients can be configured :ref:`using permissions <reference-permission-notifications>`.

You can preview the emails using the manage.py :ref:`mailtexts command <reference-commands-mailtexts>`.

Email Header & Footer
---------------------

All emails are sent using these base templates. Override these to change the header, footer and formatting of the email:

- `mails/email.txt`
- `mails/email.html`


Signup Emails
-------------

.. warning::
    Never add text, that is entered during the signup process, e.g. in the comment field, to the email content.
    This could be abused to send spam.

Welcome member
^^^^^^^^^^^^^^
Trigger: Member completes the signup process

Template: ``mails/member/member_welcome.txt``

Recipients: The member who signed up

Welcome co-member
^^^^^^^^^^^^^^^^^
Trigger: Member completes the signup process where they added co-members

Template: The template depends on whether the co-member already had an account

- For new co-members: ``mails/member/co_member_welcome.txt``
- For co-members with an existing account: ``mails/member/co_added.txt``

Recipients: The co-member(s) added during the signup process

Email address confirmation
^^^^^^^^^^^^^^^^^^^^^^^^^^
Trigger: Member requests a new email address confirmation link

Template: ``mails/member/email_confirm.txt``

Recipients: The same member

Password Reset
--------------
Trigger: Member fills out the "forgot password" form

Template: ``mails/member/password_reset.txt``

Recipients: The same member

Membership Notifications
------------------------

.. _reference-notifications-member-created:

Member Created
^^^^^^^^^^^^^^
Trigger: On signal :ref:`member_created <reference-signals-member-created>`

Template: ``mails/admin/member_created.txt``

Recipients: Users with the permission :ref:`juntagrico.notified_on_member_creation <reference-permissions-notified_on_member_creation>`

.. _reference-notifications-member-canceled:

Member Canceled
^^^^^^^^^^^^^^^

Trigger: On signal :ref:`canceled <reference-signals-canceled>` from sender ``Member``

Template: ``mails/admin/member_canceled.txt``

Recipients: Users with the permission :ref:`juntagrico.notified_on_member_cancellation <reference-permissions-notified_on_member_cancellation>`


Subscription Notifications
--------------------------

.. _reference-notifications-subscription-created:

Created
^^^^^^^
Trigger: New or existing member orders a new subscription

Template: ``mails/admin/subscription_created.txt``

Recipients: Users with the permission :ref:`juntagrico.notified_on_subscription_creation <reference-permissions-notified_on_subscription_creation>`

.. _reference-notifications-subscription-part-created:

Part Created
^^^^^^^^^^^^
Trigger: Member with an existing susbcription orders a new subscription part or changes one

Template: ``mails/admin/subpart_created.txt``

Recipients: Users with the permission :ref:`juntagrico.notified_on_subscriptionpart_creation <reference-permissions-notified_on_subscriptionpart_creation>`

.. _reference-notifications-subscription-part-canceled:

Part Canceled
^^^^^^^^^^^^^
Trigger: Member cancels a subscription part or changes one, but not the entire subscription

Template: ``mails/admin/subpart_canceled.txt``

Recipients: Users with the permission :ref:`juntagrico.notified_on_subscriptionpart_cancellation <reference-permissions-notified_on_subscriptionpart_cancellation>`

.. _reference-notifications-subscription-canceled:

Canceled
^^^^^^^^
Trigger: Member cancels the entire subscription

Template: ``mails/admin/subscription_canceled.txt``

Recipients: Users with the permission :ref:`juntagrico.notified_on_subscription_cancellation <reference-permissions-notified_on_subscription_cancellation>`


Left Subscription
^^^^^^^^^^^^^^^^^
Trigger: Member leaves their subscription

Template: ``mails/member/co_member_left_subscription.txt``

Recipients: The primary member of the subscription


Depot notifications
-------------------

.. _reference-notifications-depot-change-request:

Change Request
^^^^^^^^^^^^^^
Trigger: On signal :ref:`depot_changed <reference-signals-depot_changed>` from sender ``Subscription``

Template: ``juntagrico/mails/admin/depot_changed.txt``

Recipients: Users with the permission :ref:`juntagrico.notified_on_depot_change <reference-permissions-notified_on_depot_change>`


.. _reference-notifications-depot-change-confirmation:

Change Confirmation
^^^^^^^^^^^^^^^^^^^
Trigger: On signal :ref:`depot_change_confirmed <reference-signals-depot_change_confirmed>` from sender ``Subscription``

Template: ``mails/member/depot_changed.txt``

Recipients: Primary member of the subscription with co-members in cc


Share Notifications
-------------------

Ordered
^^^^^^^
Trigger: Member orders a share for themselves or their co-members

Template: ``mails/member/share_created.txt``

Recipients: The member that owns the ordered share

.. _reference-notifications-share-created:

Created
^^^^^^^
Trigger: On signal :ref:`share_created <reference-signals-share_created>`

Template: ``mails/admin/share_created.txt``

Recipients: Users with the permission :ref:`juntagrico.notified_on_share_creation <reference-permissions-notified_on_share_creation>`


.. _reference-notifications-share-canceled:

Canceled
^^^^^^^^
Trigger: None

Template: ``mails/admin/share_canceled.txt``

Recipients: Users with the permission :ref:`juntagrico.notified_on_share_cancellation <reference-permissions-notified_on_share_cancellation>`


Job Notifications
-----------------

.. _reference-notifications-job-subscribed:

Subscribed
^^^^^^^^^^
Trigger: On signal :ref:`subscribed <reference-signals-subscribed>` from sender ``Job``
if member had no assignment in job before

Templates:

- ``mails/admin/share_canceled.txt`` email to member
- ``juntagrico/mails/admin/job/signup.txt`` email to contact of the job

Recipients:

- Member that signup up for the job
- Contact of the job. Falls back to contact(s) of job type or area that display their email.

Reminder
^^^^^^^^
Trigger: Via cron job, 2 days before job starts

Template: ``mails/member/job_reminder.txt``

Recipient: All member that are signup up for the job

.. _reference-notifications-job-time-changed:

Job time changed
^^^^^^^^^^^^^^^^
Trigger: On signal :ref:`job_time_changed <reference-signals-job_time_changed>` from sender ``RecuringJob`` or ``OneTimeJob``

Template: ``mails/member/job_time_changed.txt``

Recipient: All member that are signup up for the job

.. _reference-notifications-job-canceled:

Canceled
^^^^^^^^
Trigger: On signal :ref:`job_canceled <reference-signals-job_canceled>` from sender ``RecuringJob`` or ``OneTimeJob``

Template: ``mails/member/job_canceled.txt``

Recipient: All member that are signup up for the job

.. _reference-notifications-job-subscription-changed:

Job Subscription changed
^^^^^^^^^^^^^^^^^^^^^^^^
Trigger: On signal :ref:`subscribed <reference-signals-subscribed>` from sender ``Job``
if member had assignment(s) in job before and still has assignment(s) after the change

Templates:

- ``juntagrico/mails/member/job/subscription_changed.txt`` email to member
- ``juntagrico/mails/admin/job/changed_subscription.txt`` email to contact of the job

Recipients:

- Member that changed their subscription to the job
- Contact of the job. Falls back to contact(s) of job type or area that display their email.

.. _reference-notifications-job-unsubscribed:

Unsubscribed from assignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Trigger: On signal :ref:`subscribed <reference-signals-subscribed>` from sender ``Job``
if member had assignment(s) in job before and has none now.

Templates:

- ``juntagrico/mails/member/job/unsubscribed.txt`` email to member
- ``juntagrico/mails/admin/job/unsubscribed.txt`` email to contact of the job

Recipients:

- Member that unsubscribed from the job
- Contact of the job. Falls back to contact(s) of job type or area that display their email.

.. _reference-notifications-job-assignment-changed:

Assignment changed
^^^^^^^^^^^^^^^^^^
Trigger: On signal :ref:`assignment_changed <reference-signals-member-assignment_changed>` from sender ``Member``
if member still has assignment(s) in job.

Templates:

- ``juntagrico/mails/member/assignment/changed.txt`` email to member
- ``juntagrico/mails/admin/assignment/changed.txt`` email to contact of the job

Recipients:

- Member whose job assignment was changed. Not sent, if member changed their own assignment.
- Contact of the job, that is not the admin who changed the assignment.
  Falls back to contact(s) of job type or area that display their email.

.. _reference-notifications-job-assignment-removed:

Assignment removed
^^^^^^^^^^^^^^^^^^
Trigger: On signal :ref:`assignment_changed <reference-signals-member-assignment_changed>` from sender ``Member``
if member has no assignments in job now.

Templates:

- ``juntagrico/mails/member/assignment/removed.txt`` email to member
- ``juntagrico/mails/admin/assignment/removed.txt`` email to contact of the job

Recipients:

- Member whose job assignment was removed. Not sent, if member removed their own assignment.
- Contact of the job, that is not the admin who changed the assignment.
  Falls back to contact(s) of job type or area that display their email.

List Notifications
------------------

.. _reference-notifications-depot-list-generated:

Depot lists generated
^^^^^^^^^^^^^^^^^^^^^
Trigger: After executing the default depot list generator.

Template: ``mails/admin/depot_list_generated.txt``

Recipients: Users with the permission :ref:`juntagrico.depot_list_notification <reference-permissions-depot_list_notification>`
