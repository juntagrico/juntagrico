.. _reference-signals:

Signals
=======

Django includes a `signal dispatcher <https://docs.djangoproject.com/en/4.2/topics/signals/>`_ that allows adding reactions on certain actions easily.
Besides `djangos built-in signals <https://docs.djangoproject.com/en/4.2/ref/signals/>`_ juntagrico sends the signals below.

Job signals
-----------

.. _reference-signals-job_canceled:

job_canceled
^^^^^^^^^^^^

Trigger: Job is saved with the canceled flag set (and the flag wasn't set before).

Arguments:

* instance: The job instance that was canceled

Default receivers:

* handle_job_canceled: :ref:`Sends notification email <reference-notifications-job-canceled>` to members
  that were signed up to that job and remove them from the job.

.. _reference-signals-job_time_changed:

job_time_changed
^^^^^^^^^^^^^^^^

Trigger: Existing job is saved with a changed time field

Arguments:

* instance: The job instance whose time was changed

Default receivers:

* handle_job_time_changed: :ref:`Sends notification email <reference-notifications-job-time-changed>` to members that are signed up to that job.

.. _reference-signals-subscribed:

subscribed
^^^^^^^^^^

Sender: Job

Trigger: Member subscribes to a job or unsubscribed from it.

Arguments:

* instance: The job instance that the member subscribed to
* member: Member that subscribed to the job
* count: The number of assignments. Is 0 if the member unsubscribes completely
* initial_count: The previous number of assignments. Is 0 if member was not signed up before
* message: A message from the member

Default receivers:

* on_job_subscribed: :ref:`Sends confirmation <reference-notifications-job-subscribed>` to member and notification to admin.


Subscription signals
--------------------

sub_created
^^^^^^^^^^^

Trigger: A new subscription has been saved.

Arguments:

* instance: The subscription instance that was created

Default receivers:

* handle_sub_created: No action.


sub_activated
^^^^^^^^^^^^^

Trigger: A subscription, where deactivation date and activation date was not set already, is being saved with an activation date.

Arguments:

* instance: The subscription instance that was changed

Default receivers:

* handle_sub_activated: Checks that none of the members has overlapping subscriptions when this one is activated, and raises an exception otherwise.
  Sets the activation date of the parts and the join date of the members according to the new activation date.


sub_deactivated
^^^^^^^^^^^^^^^

Trigger: A subscription, where deactivation date was not set already, is being saved with a deactivation date.

Arguments:

* instance: The subscription instance that was changed

Default receivers:

* handle_sub_deactivated: Sets leave date of all members of subscription to the deactivation date.
  Sets the deactivation date of active parts and deletes parts that have not been active yet.


sub_canceled
^^^^^^^^^^^^

Trigger: A subscription, where cancellation date was not set already, is being saved with a cancellation date.

Arguments:

* instance: The subscription instance that was changed

Default receivers:

* handle_sub_canceled: Sets cancellation date of all active parts of subscription and deletes the not yet active parts.


.. _reference-signals-depot_changed:

depot_changed
^^^^^^^^^^^^^

Trigger: A member requests to change their depot

Arguments:

* subscription: The subscription instance on which the depot should be changed
* member: Member that requested the depot change
* old_depot: Original depot of the subscription
* new_depot: Newly requested depot of the subscription
* immediate: True, if the change was performed automatically. This is done, when the subscription is not yet activated.

Default receivers:

* on_depot_changed: :ref:`Notify <reference-notifications-depot-change-request>` users
  with permission :ref:`notified_on_depot_change <reference-permissions-notified_on_depot_change>` via email.


.. _reference-signals-depot_change_confirmed:

depot_change_confirmed
^^^^^^^^^^^^^^^^^^^^^^

Triggers:

* Depot lists are generated using the management command `generate_depot_list` without the `--no-future` flag
* Admin confirms the depot change in the management list.

Arguments:

* instance: The subscription instance on which the depot change was confirmed

Default receivers:

* on_depot_change_confirmed: :ref:`Notify <reference-notifications-depot-change-confirmation>` Member
  and co-members of the subscription about the change.

Extra subscription signals
--------------------------

extra_sub_activated
^^^^^^^^^^^^^^^^^^^

Trigger: None

extra_sub_deactivated
^^^^^^^^^^^^^^^^^^^^^

Trigger: None


Subscription part signals
-------------------------

sub_part_activated
^^^^^^^^^^^^^^^^^^

Trigger: A subscription part, where deactivation and activation date were not set already, is being saved with an activation date.

Arguments:

* instance: The subscription part instance that was changed

Default receivers: None


sub_part_deactivated
^^^^^^^^^^^^^^^^^^^^

Trigger: A subscription part, where deactivation was not set already, is being saved with a deactivation date.

Arguments:

* instance: The subscription part instance that was changed

Default receivers: None


Share signals
-------------

.. _reference-signals-share_created:

share_created
^^^^^^^^^^^^^

Trigger: A new share has been saved.

Arguments:

* instance: The share instance that was created

Default receivers:

* handle_share_created: :ref:`Notify <reference-notifications-share-created>` users
  with permission :ref:`notified_on_share_creation <reference-permissions-notified_on_share_creation>` via email.

share_canceled
^^^^^^^^^^^^^^

Trigger: None


Member signals
--------------

.. _reference-signals-member-created:

member_created
^^^^^^^^^^^^^^

Trigger: A new member has been saved.

Arguments:

* instance: The member instance that was created

Default receivers:

* handle_member_created: :ref:`Notify <reference-notifications-member-created>` users
  with permission :ref:`notified_on_member_creation <reference-permissions-notified_on_member_creation>` via email.


member_canceled
^^^^^^^^^^^^^^^

.. warning::
    Deprecated since version 1.7.0. Use :ref:`canceled <reference-signals-canceled>` with sender ``Member`` instead.


Trigger: A member that had no cancellation date set, is saved with a cancellation date.

Arguments:

* instance: The member instance that was changed

Default receivers: None

.. _reference-signals-canceled:

canceled
^^^^^^^^

Sender: Member

Trigger: Member cancels their membership

Arguments:

* instance: The member instance of the member that canceled
* message (optional): The message the member left on cancellation

Default receivers:

* on_member_canceled: :ref:`Notify <reference-notifications-member-canceled>` users with
  permission :ref:`notified_on_member_cancellation <reference-permissions-notified_on_member_cancellation>` via email.

member_deactivated
^^^^^^^^^^^^^^^^^^

Trigger: A member that had no deactivation date set, is saved with a deactivation date.

Arguments:

* instance: The member instance that was changed

Default receivers:

* handle_member_deactivated: Remove the member from all activity areas.

.. _reference-signals-member-assignment_changed:

assignment_changed
^^^^^^^^^^^^^^^^^^

Trigger: A user with permission changed the job assignments of a member on the job page.

Arguments:

* instance: The member instance whose assignment was changed
* job: job of the changed assignments
* editor: User who changed the assignment
* count: New number of assignments of member on this job
* initial_count: Original number of assignments of member on this job
* message: Message entered by the editor.

Default receivers:

* on_assignment_changed: :ref:`Inform member and job contact <reference-notifications-job-assignment-changed>` about the changed assignments
