1.2 Release Notes
==================

1.2.3
-----
Has Migrations

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^

* Updated subscription management
   * Added subscription parts as through model for the subscription - type mapping
   * Removed all active and cancelled flags. From now on only the corresponding dates are used to calculate the state of a subscription, extrasubscrion or subscription part.
   * The new permissions for the subscription part model must be given to the users that manage subscriptions
* Enabled emails to job participants for area admin
* More display and filter fields as well as new help texts in the admin section
* Recurring jobs can now override the duration for specific instances
* Show share id on the export
* Added FROM_FILTER setting
* Email sending has been completely overhauled, including grouping certain emails in threads
* Added documentation for theming an juntagrico instance
* Rewrite of depot list generation to be more performant and extensible
* Allow to disable email in management list
* Refactor of subscription part selection using form objects

Fixes
^^^^^
* Fix in subscription part selection (only integers allowed)
* Fix in share created mail
* Fix for email address parsing for python 3.8
* Fix in depot list change
* Prevent job overassignment
* Fixes in job overview page
* Various timezone related fixes
* Using logging instead of print in all places
* Minor bugfixes and fixed typos


1.2.2
-----
Has migrations

* Various date related fixes for subscription change cancellation and job copying
* Recuring jobs can no have instance specific additional descriptions
* Extra subscription and types can now be hidden on the depot list
* The depot overview list is now grouped by day and contains a total
* Jobs can now have an infinite number of participants
* Job types can be hidden
* Fix for the coordinator bug


1.2.1
-----
Has no migrations

* Fix in subscription change view bug from version 1.2.0


1.2.0
-----
Has migrations

* Mailer code refactored, new permissions to be notified when a member, subscription or share is created or canceled
* Jobs are visible if they are on the same day even if they have already started
* Job time changed bugfix
* Removed google maps and corresponding setting
* Members can leave subscription
* Main member can be changed by Members themselfes
* Non share holders are deactivated when subscription is deactivated
* Better gender texts
* Billing stubs are remoived to extension
* Fix in upcoming jobs widget
* Fix in cancelation date calculation
* Fix in Co Member adding
