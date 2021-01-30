1.1 Release Notes
==================

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
