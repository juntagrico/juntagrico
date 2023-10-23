.. _reference-signals:

Signals
=======

Django includes a `signal dispatcher <https://docs.djangoproject.com/en/4.2/topics/signals/>`_ that allows adding reactions on certain actions easily.
Besides `djangos built-in signals <https://docs.djangoproject.com/en/4.2/ref/signals/>`_ juntagrico sends the signals below.

Job signals
-----------

job_canceled
^^^^^^^^^^^^

Trigger: Job is saved with the cancelled flag set (and the flag wasn't set before).

Arguments:

* instance: The job instance that was cancelled

Default receivers:

* handle_job_canceled: Send notification email to members that were signed up to that job and remove them from the job.

job_time_changed
^^^^^^^^^^^^^^^^

Trigger: Existing job is saved with a changed time field

Arguments:

* instance: The job instance whose time was changed

Default receivers:

* handle_job_time_changed: Send notification email to members that are signed up to that job.


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

share_created
^^^^^^^^^^^^^

Trigger: A new share has been saved.

Arguments:

* instance: The share instance that was created

Default receivers:

* handle_share_created: Send email to admins, that share has been created

share_canceled
^^^^^^^^^^^^^^

Trigger: None


Member signals
--------------

member_created
^^^^^^^^^^^^^^

Trigger: A new member has been saved.

Arguments:

* instance: The member instance that was created

Default receivers:

* handle_member_created: Send email to admins, that member has been created


member_canceled
^^^^^^^^^^^^^^^

Trigger: A member that had no cancellation date set, is saved with a cancellation date.

Arguments:

* instance: The member instance that was changed

Default receivers: None


member_deactivated
^^^^^^^^^^^^^^^^^^

Trigger: A member that had no deactivation date set, is saved with a deactivation date.

Arguments:

* instance: The member instance that was changed

Default receivers:

* handle_member_deactivated: Remove the member from all activity areas.
