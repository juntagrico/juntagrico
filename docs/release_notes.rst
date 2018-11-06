Release Notes
=============

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

1.1.4
-----
 Has migrations

* Fixed profile error
* IBAN field not nullable blank used for no value


1.1.4
-----
 Has migrations

* Fixed various errors and bugs in the onboarding process
* Other various bugfixes


Dev
-----
 Has migrations

* Work in progress
* Ability to display messages at the bottom of depot lists. Added in the data administration.
* Area admins are now informed when a member leaves their activity area
* New setting ORGANISATION_NAME_CONFIG to enrich the organisation name
* made texts mor neutral on context of the organisation type
* removed the MEMBER_STRING, MEMBERS_STRING, ASSIGNMENT_STRING and ASSIGNMENTS_STRING for the VOCABULARY setting
* added new setting ENABLE_SHARES to enable or disable all share related functions
* upgrade to bootstrap 4.1.3
* upgraded requirements
