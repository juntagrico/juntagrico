Release Notes
=============

1.3.7
-----
Has no migrations

Fixes
^^^^^
* Add mail button for depot admins
* Fixed query for depot admin member filter

1.3.6
-----
Has no migrations

Fixes
^^^^^
* Assignments overviews only consider current business year
* Fix in export subscription
* Fix that users with filter permission can actually see the filters

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* Inconsistencies include missing primary member as error

1.3.5
-----
Has no migrations

Fixes
^^^^^
* Fix for MIME-Type picky browser
* Fix datatables dom

1.3.4
-----
Has no migrations

Fixes
^^^^^
* Fix incorrect display of email count in subscription filters
* Member filter for depots only displays members with active subscription

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* assignment counts include now planned assignments
* extracted assignment overviews into separate management list
* introduced search builder in new assignment management list
* moved general filters in corresponding management section in admin menu
* filter for all members and for active members
* streamlined the admin menu


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