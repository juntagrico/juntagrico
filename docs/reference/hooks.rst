.. _reference-hooks:

Hooks
=====

Template Hooks
--------------

register_admin_menu
^^^^^^^^^^^^^^^^^^^
  Renders the given template at the end of the admin menu.

  Arguments:

  - template: String

register_admin_subscription_menu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  Renders the given template at the end of the subscription section in the admin menu.

  Arguments:

  - template: String

register_show_admin_menu_method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  If the added function returns true, the admin menu will be displayed

  Arguments:

  - function: Function that takes user as first argument

register_user_menu
^^^^^^^^^^^^^^^^^^
  Renders the given template at the end of the user menu.
  
  Arguments:

  - template: String

register_sub_overview
^^^^^^^^^^^^^^^^^^^^^
  Renders the given template at the end of the subscription overview page

  Arguments:

  - template: String

register_sub_change
^^^^^^^^^^^^^^^^^^^
  Renders the given template at the end of the subscription overview page

  Arguments:

  - template: String

Admin Hooks
-----------

register_model_inline
^^^^^^^^^^^^^^^^^^^^^
  Adds the given inline to the admin of the given model

  Arguments:

  - model: String
  - inline: InlineModelAdmin

Config Hooks
------------

register_config_class
^^^^^^^^^^^^^^^^^^^^^
  Extends the juntagrico ``config`` template tag by the attributes of the given class

  Arguments:

  - cls: Class

register_version
^^^^^^^^^^^^^^^^
  Shows the given version with the given name on the version page

  Arguments:

  - name: String
  - version: String
