Release Notes
=============

1.4.0
-----
Has  migrations

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* Member Features:
    * Share certificate download

* Admin Features:
    * Added possibility to hide depots from depot list
    * Added sorting in the data administration for depot, area, extrasubscription type and category, list messages as well as subscription type and product
    * New setting SUB_OVERVIEW_FORMAT for the formatting of the subscription overview
    * Added special role for notification on depot list generation
    * Added value field for shares

* Developer Features:
    * Menu dict method eliminated for easier view creation and performance improvements

Fixes
^^^^^
* Fix in member user relation to prevent members without an user
* Fix JobExtra(Type) labels in admin
* Take remaining core assignments into account in assignment widget
