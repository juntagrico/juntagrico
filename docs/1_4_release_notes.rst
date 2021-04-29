Release Notes
=============

1.4.0
-----
Has  migrations

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* Member Features:
    * Share certificate download
    * Shares have now two new fields to be compliant with the german coop law

* Admin Features:
    * Extra subscription are now subscription parts, while products can now be marked as extra subscription products. Check the newly created products, sizes, and types
    * Billing üeriods are now available on all subscription types. If no period is defined the price will be taken into account specified in the type. Otherwise the price in the type will be ignored and the prices from the periods will be taken into account.
    * The admin menu is now configured using new permissions. For the menu items managing an entity the user need the change_[entity] permission. For the exports and list menu items the new permissions can_view_lists and can_view_exports are introduced. The old can_filter_[entity] permissions are still in place and valid. 
    * Added possibility to hide depots from depot list
    * Added sorting in the data administration for depot, area, extrasubscription type and category, list messages as well as subscription type and product
    * New setting SUB_OVERVIEW_FORMAT for the formatting of the subscription overview
    * Added special role for notification on depot list generation
    * Added value field for shares
    * Job duration is now a floating point value
    * Deactivated subscription can only be edited if the user has the can_change_deactivated_subscriptions permission
    * Past jobs can only be edited if the user has the can_edit_past_jobs permission
    * Depot has now a special field for access information

* Developer Features:
    * Added django-admin-sortable2, therefore add 'adminsortable2' to the INSTALLED_APPS setting
    * Menu dict method eliminated for easier view creation and performance improvements
    * Moved to BigAutofield for ids
    * Upgraded tynimce to version 5.7.1
    * template tags are now unde juntagrico. For example former ``{% load config %}`` becomes ``{% load juntagrico.config %}``
    * all juntagrico static files are now under ''static/juntagrico''

Fixes
^^^^^
* Fix in member user relation to prevent members without an user
* Fix JobExtra(Type) labels in admin
* Take remaining core assignments into account in assignment widget
* Depot list overview generation date is now properly placed
