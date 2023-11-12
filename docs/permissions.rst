Permissions
===========

Overview
--------
juntagrico relies heavily on the Django permission mechanism to customize the system for different users. In this chapter we will explain which permissions can be used for customization and how they work.

Grant Permissions
-----------------
Permissions are granted in the admin part of juntagrico, which in fact is the admin part of Django. To grant someone a permission, the persons ``User`` has to be edited.
You find a link to a members user instance in the member admin form.
There you can search for a permission and add it to the user using the little right arrow next to it. Do not forget to save the user in order for the permissions to take effect.
You can also create groups of permissions which can be assigned to single users. If you need more information on that check out the Django documentation concerning permissions.

Area and Depot Admins
---------------------
juntagrico.is_depot_admin
^^^^^^^^^^^^^^^^^^^^^^^^^
Should be assigned to members which are administator of a depot, so that they can filter and communicate with the members in their depot.

Search Hints:
    * German: Benutzer ist Depot Admin

juntagrico.is_area_admin
^^^^^^^^^^^^^^^^^^^^^^^^
Should be assigned to members which are administator of an activity area, so that they can filter and communicate with the members in their area.
Also it allows them to create new jobs and comunicate with the members participating in one of the jobs of their area.

Search Hints:
    * German: Benutzer ist Tätigkeitsbereichskoordinator

Notifications
-------------
Some entities send a notification email when they are created or cancelled. Should a member be notified on a certain event it has to have the corresponding
permission for that entity type and event.

juntagrico.notified_on_share_creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member gets notified when a share is created.

Search Hints:
    * German: Erstellung informiert

juntagrico.notified_on_share_cancellation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member gets notified when a share is cancelled.

Search Hints:
    * German: Kündigung informiert

juntagrico.notified_on_member_creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member gets notified when a member is created.

Search Hints:
    * German: Erstellung informiert

juntagrico.notified_on_member_cancellation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member gets notified when a member cancels his membership.

Search Hints:
    * German: Kündigung informiert

juntagrico.notified_on_subscription_creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member gets notified when a subscription is created.

Search Hints:
    * German: Erstellung informiert

juntagrico.notified_on_subscription_cancellation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member gets notified when a subscription is cancelled.

Search Hints:
    * German: Kündigung informiert

juntagrico.depot_list_notification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member gets notified when the depot list is generated.

Search Hints:
    * German: Listen-Erstellung informiert

Administrator Menu
------------------
Which entries can be seen on the administration menu depepend on a set of permissions.

juntagrico.change_subscription
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member sees the subscription entry in the administration menu.

Search Hints:
    * German: Abo

juntagrico.change_subscriptionpart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member sees the extra subscription entry in the administration menu.

Search Hints:
    * German: Bestandteil

juntagrico.change_member
^^^^^^^^^^^^^^^^^^^^^^^^
Member sees the member entry in the administration menu.

Search Hints:
    * German: Mitglied

juntagrico.change_assignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member sees the assignment entry in the administration menu.

Search Hints:
    * German: Arbeitseinsatz

juntagrico.change_share
^^^^^^^^^^^^^^^^^^^^^^^
Member sees the share entry in the administration menu.

Search Hints:
    * German: Anteilsschein

juntagrico.can_send_mails
^^^^^^^^^^^^^^^^^^^^^^^^^
Member can access the mail from from the administration menu.

Search Hints:
    * German: Emails versenden

juntagrico.can_view_lists
^^^^^^^^^^^^^^^^^^^^^^^^^
Member sees the lists entry in the administration menu.

Search Hints:
    * German: Listen öffnen

juntagrico.can_view_exports
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member sees the exports entry in the administration menu.

Search Hints:
    * German: Exporte öffnen

juntagrico.can_filter_members
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member sees the member filter entry in the administration menu without the permission to change members.

Search Hints:
    * German: filtern

juntagrico.can_filter_subscriptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member sees the subscription filter entry in the administration menu without the permission to change subscriptions.

Search Hints:
    * German: filtern

Email Permissions
-----------------
juntagrico.can_use_general_email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member can use the email address specified in the setting :ref:`INFO_EMAIL` as sender in the mail form.

Search Hints:
    * German: General Email

Edit Permissions
----------------
juntagrico.can_edit_past_jobs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member can edit jobs which are in the past.

Search Hints:
    * German: vergangene

juntagrico.can_change_deactivated_subscriptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Member can edit subscriptions which are deactivated.

Search Hints:
    * German: deaktivierte

Dependent Permissions
---------------------
In order to be able to edit some types of entites not only the ``change`` permission of this entity type has to be granted to a member but also
some dependent permissions.

Subscription
^^^^^^^^^^^^
Also requires change permissions for subscription parts and subscription membership.

Jobs
^^^^
Also requires change permission for assignments and job extras.

Deliveries
^^^^^^^^^^
Also requires change permission for deliver item.
