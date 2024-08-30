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

Add Users to the group
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

Dependent Permissions
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

juntagrico.is_area_admin
^^^^^^^^^^^^^^^^^^^^^^^^
Should be assigned to members which are administrator of an activity area, so that they can filter and communicate with the members in their area.
Also it allows them to create new jobs and communicate with the members participating in one of the jobs of their area.

Search Hints:
    * German: Benutzer ist Tätigkeitsbereichskoordinator


.. _reference-notifications:

Notifications
-------------
Some entities send a notification email when they are created or cancelled. Should a member be notified on a certain event it has to have the corresponding
permission for that entity type and event.

juntagrico.notified_on_share_creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets notified when a share is created.

Search Hints:
    * German: Erstellung informiert

juntagrico.notified_on_share_cancellation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets notified when a share is cancelled.

Search Hints:
    * German: Kündigung informiert

juntagrico.notified_on_member_creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets notified when a member is created.

Search Hints:
    * German: Erstellung informiert

juntagrico.notified_on_member_cancellation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets notified when any member cancels their membership.

Search Hints:
    * German: Kündigung informiert

juntagrico.notified_on_subscription_creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets notified when a subscription is created.

Search Hints:
    * German: Erstellung informiert

juntagrico.notified_on_subscription_cancellation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets notified when a subscription is cancelled.

Search Hints:
    * German: Kündigung informiert

juntagrico.notified_on_subscriptionpart_creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets notified when a subscription part is created.

Search Hints:
    * German: Erstellung informiert

juntagrico.notified_on_subscriptionpart_cancellation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person gets notified when a subscription part is cancelled.

Search Hints:
    * German: Kündigung informiert

juntagrico.depot_list_notification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member gets notified when the depot list is generated.

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
Person can access the mail from from the administration menu.

Search Hints:
    * German: Emails versenden

juntagrico.can_view_lists
^^^^^^^^^^^^^^^^^^^^^^^^^
Person sees the lists entry in the administration menu.

Search Hints:
    * German: Listen öffnen

juntagrico.can_view_exports
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person sees the exports entry in the administration menu.

Search Hints:
    * German: Exporte öffnen

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
juntagrico.can_use_general_email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can use the email address specified in the setting :ref:`INFO_EMAIL <reference-settings-info-email>` as sender in the mail form.

Search Hints:
    * German: General Email


Edit Permissions
----------------
juntagrico.can_edit_past_jobs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can edit jobs which are in the past.

Search Hints:
    * German: vergangene

juntagrico.can_change_deactivated_subscriptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Person can edit subscriptions which are deactivated.

Search Hints:
    * German: deaktivierte
