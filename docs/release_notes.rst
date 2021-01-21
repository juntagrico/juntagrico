Release Notes
=============

1.3.4
-----
Has no migrations

* Fix incorrect display of email count in subscription filters

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* assignment counts include now planned assignments
* extracted assignement overviews into separate management list
* introduced search builder in new assignment management list

1.3.3
-----
Has no migrations

Fixes
^^^^^
* Fix in depot list amount overview
* rollback of xhtml2pdf version since it is not compatible with alpine linux

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* Introduces subscription excel export



1.3.2
-----
Has no migrations

Fixes
^^^^^
* Fix subscription count and depot display in member filter list
* Fix saving subscriptions with limited permissions
* Fix error when adding existing co-members with active subscriptions

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* WHITELIST_EMAILS supports now regular expressions and is now documented
* Deeper subscription inconsistency checks

1.3.1
-----
Has no migrations

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* Developer Features:
   * Upgraded requirements


1.3.0
-----
Has  migrations

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* Member Features:
   * Share management: Overview of shares & cancellation of individual shares
   * Subscription management: Option to leave a subscription
   * Show membership state on membership page
   * Set nickname for subscription as shown on depot list
   * More readable listing of subscription parts
   * Include location in job reminder email
* Admin Features:
   * History of subscription memberships & scheduling of future changes of subscription recipients
   * Shares now store the creation date
   * Filter members by permissions
   * Batch editing of dates in shares
   * Also copy unlimited places in job copying
   * Show content of future subscriptions in name
   * Check all timestamps for consistent order
* Improvements in depot list:
   * Layout optimization
   * Added vocabulary for "package" in depot list
* Developer Features:
   * Upgraded to django 3.1.x, therefore add 'django.template.context_processors.request' to the TEMPLATES setting under 'context_processors'
   * Added permissions for admin notifications on subscription part change
   * Removed job_id argument from contact-member view

Fixes
^^^^^
* Fixes in cancellation of extra subscriptions
* Hide unused products in subscription order form
* Fixed share count in subscription overview
* Fixed issue in job copying
* Fixed notification emails with no recipients
* Assert that active subscriptions have at least 1 active part
* Fix in cancellation of subscription parts
* Minor bugfixes and fixed typos


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


1.1.9
-----
Has migrations

* Added Cookie consent
* Design a bit more responsive
* Job display name used where possible
* Updated share management
* Added user management to deactivate canceled users
* Fix in welcome mail
* Fix in Subscription deactivation
* Links in emails work now also for internal links
* Old subscriptions are now visible in Member admin
* Fixed small bug in the size change


1.1.8
-----
Has no migrations

* personal template loader removed adapt your settings accordingly
* Added crispy-forms
   * Add CRISPY_TEMPLATE_PACK = 'bootstrap4' to settings
   * Add 'crispy_forms' to INSTALLED_APPS
* CSS class 'juntagrico_logo' is deprecated. Use 'juntagrico-logo' instead
* make sure users are logged out at sign up
* fix false message in job cancellation message
* added time to job search field in admin area
* fix broken deliveries
* fix text in subscription cancellation email
* fix for member add in admin area
* improvement of area overview
* descriptions allow now newlines and urls
* direct link from job overview to job entity in admin area
* job not directly deleted if members assigned
* fix for test data generation
* fix false date comparison in size change
* users can now have multiple subscriptions
* fix reply to error in mailing
* new right to edit past jobs
* reworked addons hooks, so that caching is obsolete (settings can be removed)
* fix cancelling inactive subscription fails if it has extra subs
* user menu rewrite
* lifecycle and consistency check code rewritten
* rewrote urls to use path and names
* depot list support now emojis
* major template rewrites. Check custom css besides custom logos


1.1.7
-----
Has migrations

* New setting GDPR_INFO to make it EU compliant
* Introduced Products in order to have multiple sizes for different Products. on existing Instances a default product called Product will be added
* Added gettext so that strings can be translated
* Texts where adapted
* Shares are controlled more thoroughly if enabled
* Possibility to easily pay back canceled shares by generating iso20022 pain001 xml file
* Only active subscriptions and members are shown in the filters
* Better sorting in the filters, also added textmarkers to be able to use better regex filtering
* Next jobs bug fixed so that all see there next jobs
* Subscription list bug with the duplicate subscription was fixed
* More information shown for Assignemnts on the admin overview page
* upgraded requirements
* added menu hooks for apps


1.1.6
-----
Has migrations

* Work in progress
* Ability to display messages at the bottom of depot lists. Added in the data administration.
* Area admins are now informed when a member leaves their activity area
* New setting ORGANISATION_NAME_CONFIG to enrich the organisation name
* made texts more neutral on context of the organisation type
* removed the MEMBER_STRING, MEMBERS_STRING, ASSIGNMENT_STRING and ASSIGNMENTS_STRING for the VOCABULARY setting
* added new setting ENABLE_SHARES to enable or disable all share related functions
* upgrade to bootstrap 4.1.3
* upgraded requirements
* added possibility to imitate special dates when activating and deactivating subscriptions and extrasubscriptions
* overhauled mail stuff. possibility to exchange mail sending code with the following setting DEFAULT_MAILER
* new setting ENABLE_REGISTRATION
* possibility to hide subscription sizes in subscription creation


1.1.5
-----
Has migrations

* Fixed various errors and bugs in the onboarding process
* Other various bugfixes


1.1.4
-----
Has migrations

* Fixed profile error
* IBAN field not nullable blank used for no value


1.1.3
-----
No migrations

* Fixed Typo in Billable
* Empty strings as default for settings containing an url t a document
* Empty url configs prevent link from being displayed in templates
* fix for writing list and paid shares
* empty strings in profile IBAN field form are not validated anymore
* doc updated
* error in onetime job fixed
