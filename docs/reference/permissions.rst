.. _reference-permissions:

Permissions
===========

.. note::
    Permissions are named in the language of your instance and use your terminology.

juntagrico relies heavily on the Django permission mechanism to customize the system for different users.
In this chapter we will explain which permissions can be used for customization and how they work.

Grant Permissions
-----------------

Create a group
^^^^^^^^^^^^^^

1. Login with a super admin user.
2. Open the data management ("Datenverwaltung") -> Groups -> Add to create a new group or edit an existing one.
3. Set a name for the group, e.g. "share management".
4. Select and add the permissions (using the arrow to the right in the middle) that you want to give to this group and save the group.

What Permissions do I need to set?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are 4 basic permissions for each entity which are self explanatory:

* View
* Add
* Change
* Delete

.. hint::
    If a user should be able to change an entity, they also need access to at least view the related entities.
    See :ref:`Dependent Permissions <reference-dependent-permissions>` below.

Juntagrico provides some additional permissions, that are described in the sections below.

Add users to the group
^^^^^^^^^^^^^^^^^^^^^^

1. Login with a super admin user.
2. Open the data management ("Datenverwaltung") -> User ("Benutzer") and edit the user of the member you want to give the permissions to.
3. If the user needs access to the data management, tick staff status ("Mitarbeiter-Status").
4. Add the relevant groups for this user and save the user.

You may also give permissions do users directly but this is not recommended as it is then harder to transfer the same permissions to another user.

Testing the user access
^^^^^^^^^^^^^^^^^^^^^^^

To be sure, that the user can do what you intended them to do, it is best to create a test user and give them the same permissions.
Try out all actions with the test user, to confirm that they work.

.. note::
    You can also test the permissions of a user by impersonating them. However, by default the data admin is excluded from impersonation.
    If you want to check the users permissions in the data admin as well, set the ``IMPERSONATE_URI_EXCLUSIONS`` setting to an empty list.
    `Read more <https://code.netlandish.com/~petersanchez/django-impersonate/#settings>`_.


.. _reference-dependent-permissions:

Staff status and superuser status
---------------------------------

In addition to the permissions a user can be granted staff status ("Mitarbeiter-Status") and superuser status ("Administrator-Status").
These have the following effects:

- staff status: Allows the user to login to the django admin page ("Datenverwaltung"), to see which version of juntagrico is installed and to contact any member via email.
- superuser status: Grants the user all permissions, except the notification permissions, which need to be granted specifically.

Dependent permissions
---------------------
In order to be able to edit some types of entities not only the ``change`` permission of this entity type has to be granted to a member but also
some dependent permissions.

Subscription
^^^^^^^^^^^^
Also requires change permissions for subscription parts and subscription membership.
And view permission for members.

Jobs
^^^^
Also requires change permission for assignments and job extras.
And view permission for job types and members.

Job Types
^^^^^^^^^
Also require at least view permission for locations.

Depot
^^^^^
Also require at least view permission for locations.

Deliveries
^^^^^^^^^^
Also requires change permission for deliver item.

Shares
^^^^^^
Also require at least view permission for members.


Area and Depot Admins
---------------------
juntagrico.is_depot_admin
^^^^^^^^^^^^^^^^^^^^^^^^^
Should be assigned to members which are administrator of a depot, so that they can filter and communicate with the members in their depot.

Search Hints:
    * German: Benutzer ist Depot Admin

Area Coordinators
^^^^^^^^^^^^^^^^^

.. warning::
    Changed in 2.0: Permission `juntagrico.is_area_admin` was removed.

Area coordinator permissions are configured for each area and coordinator individually.
These permissions can be set when editing an area in the data management ("Datenverwaltung") -> Activity Area ("Tätigkeitsbereiche").
There you can add a coordinator and distribute the following permissions.

- Can modify area: Coordinator can change the description and the contact(s) of this area
- Can see members: Coordinator can see the list of members that participate in this activity area
- Can contact members: Coordinator can see names, email addresses and phone numbers of area participants and can contact participants of jobs in their area
- Can remove members: Coordinator can remove participants from this area
- Can manage jobs: Coordinator can create and modify all jobs of this area
- Can manage assignments: Coordinator can change and remove assignments of jobs in this area


.. _reference-permission-notifications:

Notifications
-------------
Some entities send a notification email when they are created or canceled.
Should a member be notified on a certain event it has to have the corresponding
permission for that entity type and event.

.. note::
    These permissions need to be given explicitly, i.e., administrators are not notified implicitly.


.. _reference-permissions-notified_on_share_creation:

juntagrico.notified_on_share_creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets :ref:`notified <reference-notifications-share-created>` when a share is created.

Search Hints:
    * German: Erstellung informiert

.. _reference-permissions-notified_on_share_cancellation:

juntagrico.notified_on_share_cancellation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets :ref:`notified <reference-notifications-share-canceled>` when a share is canceled.

Search Hints:
    * German: Kündigung informiert

.. _reference-permissions-notified_on_member_creation:

juntagrico.notified_on_member_creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets :ref:`notified <reference-notifications-member-created>` when a member is created.

Search Hints:
    * German: Erstellung informiert

.. _reference-permissions-notified_on_member_cancellation:

juntagrico.notified_on_member_cancellation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets :ref:`notified <reference-notifications-member-canceled>` when any member cancels their membership.

Search Hints:
    * German: Kündigung informiert

.. _reference-permissions-notified_on_subscription_creation:

juntagrico.notified_on_subscription_creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets :ref:`notified <reference-notifications-subscription-created>` when a subscription is created.

Search Hints:
    * German: Erstellung informiert

.. _reference-permissions-notified_on_subscription_cancellation:

juntagrico.notified_on_subscription_cancellation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets :ref:`notified <reference-notifications-subscription-canceled>` when a subscription is canceled.

Search Hints:
    * German: Kündigung informiert

.. _reference-permissions-notified_on_subscriptionpart_creation:

juntagrico.notified_on_subscriptionpart_creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets :ref:`notified <reference-notifications-subscription-part-created>` when a subscription part is created.

Search Hints:
    * German: Erstellung informiert

.. _reference-permissions-notified_on_subscriptionpart_cancellation:

juntagrico.notified_on_subscriptionpart_cancellation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets :ref:`notified <reference-notifications-subscription-part-canceled>` when a subscription part is canceled.

Search Hints:
    * German: Kündigung informiert

.. _reference-permissions-notified_on_depot_change:

juntagrico.notified_on_depot_change
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets :ref:`notified <reference-notifications-depot-change-request>` when a member wants to change their depot.

Search Hints:
    * German: Änderung informiert

.. _reference-permissions-depot_list_notification:

juntagrico.depot_list_notification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member gets :ref:`notified <reference-notifications-depot-list-generated>` when the depot list is generated.

Search Hints:
    * German: Listen-Erstellung informiert


Administrator Menu
------------------
Which entries can be seen on the administration menu depend on a set of permissions.

juntagrico.change_subscription
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person sees the subscription entry in the administration menu.

Search Hints:
    * German: Abo

juntagrico.change_subscriptionpart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person sees the extra subscription entry in the administration menu.

Search Hints:
    * German: Bestandteil

juntagrico.change_member
^^^^^^^^^^^^^^^^^^^^^^^^
Person sees the member entry in the administration menu.

Search Hints:
    * German: Mitglied

juntagrico.change_assignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person sees the assignment entry in the administration menu.

Search Hints:
    * German: Arbeitseinsatz

juntagrico.change_share
^^^^^^^^^^^^^^^^^^^^^^^
Person sees the share entry in the administration menu.

Search Hints:
    * German: Anteilsschein

juntagrico.can_send_mails
^^^^^^^^^^^^^^^^^^^^^^^^^
Person can access the email form in the administration menu.

Search Hints:
    * German: Emails versenden

juntagrico.can_email_all_in_system
^^^^^^^^^^^^^^^^^^^^^^^^^
Person can send emails to all active users in the system via the email form.

Requires:
    * juntagrico.can_send_mails

Search Hints:
    * German: Emails versenden

juntagrico.can_email_all_with_share
^^^^^^^^^^^^^^^^^^^^^^^^^
Person can send emails to all users with active shares via the email form.

Requires:
    * juntagrico.can_send_mails

Search Hints:
    * German: Emails versenden

juntagrico.can_email_all_with_sub
^^^^^^^^^^^^^^^^^^^^^^^^^
Person send emails to all users with active subscription via the email form.

Requires:
    * juntagrico.can_send_mails

Search Hints:
    * German: Emails versenden

juntagrico.can_email_free_address_list
^^^^^^^^^^^^^^^^^^^^^^^^^
Person send mails to a any manual list of addresses via the email form.

Requires:
    * juntagrico.can_send_mails

Search Hints:
    * German: Emails versenden

juntagrico.can_view_lists
^^^^^^^^^^^^^^^^^^^^^^^^^
Person can open the generated lists in the administration menu.

Search Hints:
    * German: Benutzer kann Listen öffnen

juntagrico.can_generate_lists
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can generate lists (of depot etc.)

Search Hints:
    * German: Benutzer kann Listen erzeugen

juntagrico.can_view_exports
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person sees the exports entry in the administration menu.

Search Hints:
    * German: Benutzer kann Exporte öffnen

juntagrico.can_filter_members
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person sees the member filter entry in the administration menu without the permission to change members.

Search Hints:
    * German: filtern

juntagrico.can_filter_subscriptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person sees the subscription filter entry in the administration menu without the permission to change subscriptions.

Search Hints:
    * German: filtern


Email Permissions
-----------------
These permissions are related to sending emails.

juntagrico.can_use_general_email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can use the "general" email address specified in the setting :ref:`CONTACTS <reference-settings-contacts>` as sender in the mail form.

Search Hints:
    * German: Benutzer kann allgemeine E-Mail-Adresse verwenden

juntagrico.can_use_for_members_email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can use the "for_member" email address specified in the setting :ref:`CONTACTS <reference-settings-contacts>` as sender in the mail form.

Search Hints:
    * German: Benutzer kann E-Mail-Adresse "for_members" verwenden

juntagrico.can_use_for_subscriptions_email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can use the "for_subscriptions" email address specified in the setting :ref:`CONTACTS <reference-settings-contacts>` as sender in the mail form.

Search Hints:
    * German: Benutzer kann E-Mail-Adresse "for_subscription" verwenden

juntagrico.can_use_for_shares_email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can use the "for_shares" email address specified in the setting :ref:`CONTACTS <reference-settings-contacts>` as sender in the mail form.

Search Hints:
    * German: Benutzer kann E-Mail-Adresse "for_shares" verwenden

juntagrico.can_use_technical_email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can use the "technical" email address specified in the setting :ref:`CONTACTS <reference-settings-contacts>` as sender in the mail form.

Search Hints:
    * German: Benutzer kann technische E-Mail-Adresse verwenden

juntagrico.can_email_attachments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Person can add attachments when sending an email via the member contact form.

Search Hints:
    * German: Benutzer kann Anhänge per E-Mail senden


Edit Permissions
----------------
These permissions allow to edit certain entities.

juntagrico.can_edit_past_jobs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can edit jobs which are in the past.

Search Hints:
    * German: vergangene

juntagrico.change_assignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can edit all assignments on all jobs.
To reduce the assignments, the `juntagrico.delete_assignment` permission is needed. See below.

Search Hints:
    * German: Arbeitseinsatz

juntagrico.delete_assignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can remove any assignment on any job.

Search Hints:
    * German: Arbeitseinsatz

juntagrico.can_change_deactivated_subscriptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can edit subscriptions which are deactivated.

Search Hints:
    * German: deaktivierte

Other Permissions
-----------------

juntagrico.is_operations_group
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::
    Deprecated. This permission will be replaced by more granular permissions in the next releases.

- Download payment file for shares
- (De)activate subscriptions

Search Hints:
    * German: Benutzer ist in der BG
