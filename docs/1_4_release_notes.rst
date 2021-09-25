Release Notes
=============

Dev
---

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* Member Features:
    * Filter for free slots on jobs
    * Show less and clearer messages on job page
    * Clarify some texts

* Developer Features:
    * Support for Python 3.9 and dropped support for python 3.6 and 3.7

Fixes
^^^^^
* Fix editing limitations for past jobs and deactivated subs
* Made email uniqueness check case-insensitive
* Only show depot access information for current depot
* Use informal language consistently in password reset process
* Menu fixes:
  * Make assignment admin menu entry visible as documented
  * Highlight jobs menu entry when page is active
  * Fix view access to match menu visibility
* Fix membership cancellation
* Upgraded datatables.js to fix issue with search builder on Safari


1.4.1
-----

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* Member Features:
    * Better password reset process
* Admin Features:
    * Documentation on :doc:`Permissions`
* Fixes:
    * Fix in share payout



1.4.0
-----
Has migrations

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* Upgrade Instructions:
    * Added django-admin-sortable2, therefore add 'adminsortable2' to the INSTALLED_APPS setting
    * You may have to add permissions to users to restore their admin menu visibility and ability to edit some entities. See below.
    * If you overrode templates, you will have to move and update them
        * Template tags are now namespaced in juntagrico. For example former ``{% load config %}`` becomes ``{% load juntagrico.config %}``
        * All juntagrico static files are now namespaced and can be found in ''static/juntagrico''
        * Menu dict method eliminated for easier view creation and performance improvements

* Member Features:
    * Share certificate download
    * Shares now have two new fields to be compliant with the german coop law

* Admin Features:
    * Extra subscription are now subscription parts, while products can now be marked as extra subscription products. Check the automatically migrated products, sizes, and types
    * Billing periods are now available on all subscription types. If no period is defined the price will be taken into account specified in the type. Otherwise the price in the type will be ignored and the prices from the periods will be taken into account.
    * The admin menu visibility is now configured using new permissions.
        * For the menu items managing an entity the user need the `change_[entity]` permission.
        * For the exports and list menu items the new permissions `can_view_lists` and `can_view_exports` are introduced.
        * The old `can_filter_[entity]` permissions are still in place and valid.
    * Added possibility to hide depots from depot list
    * Added sorting in the data administration for depot, area, extrasubscription type and category, list messages as well as subscription type and product
    * New setting :ref:`SUB_OVERVIEW_FORMAT` for the formatting of the subscription overview
    * Added special role for notification on depot list generation
    * Added value field for shares
    * Job duration is now a floating point value
    * Text fields can now contain html code
    * Deactivated subscription can only be edited if the user has the `can_change_deactivated_subscriptions` permission
    * Past jobs can only be edited if the user has `the can_edit_past_jobs` permission
    * Depot has now a special field for access information that is only shown to members of that depot
    * New Setting :ref:`DEFAULT_DEPOTLIST_GENERATORS`

* Developer Features:
    * Moved to BigAutofield for ids
    * Upgraded TyniMCE to version 5.7.1
    * Added possibility to enable rich text fields in description fields. For configuration see :ref:`Rich Text Editor`

Fixes
^^^^^
* Fix in member user relation to prevent members without a user
* Fix JobExtra(Type) labels in admin
* Take remaining core assignments into account in assignment widget
* Depot list overview generation date is now properly placed in the pdf
