.. _reference-hooks:

Hooks
=====

Template Hooks
--------------

register_admin_menu
^^^^^^^^^^^^^^^^^^^

.. warning::
    Deprecated since version 1.6.0. Use :ref:`template overrides <reference-templates-extend_admin_menu>` instead.

Renders the given template at the end of the admin menu.

Arguments:

- template: String

register_admin_subscription_menu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::
    Deprecated since version 1.6.0. Use :ref:`template overrides <reference-templates-extend_admin_subscription_menu>` instead.

Renders the given template at the end of the subscription section in the admin menu.

Arguments:

- template: String

register_show_admin_menu_method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::
    Removed in juntagrico 1.6.0. Now it is enough to not add any HTML to the admin menu,
    for users without access. I.e. Add an if condition in your menu template to only show
    it to users who should have access.


register_user_menu
^^^^^^^^^^^^^^^^^^

.. warning::
    Deprecated since version 1.6.0. Use :ref:`template overrides <reference-templates-extend_user_menu>` instead.

Renders the given template at the end of the user menu.

Arguments:

- template: String

register_sub_overview
^^^^^^^^^^^^^^^^^^^^^

.. warning::
    Removed in version 1.6.0. Keep it for the legacy subscription overview.
    For the new subscription overview use :ref:`template overrides <reference-templates-extend_subscription_overview_single>` instead.

register_sub_change
^^^^^^^^^^^^^^^^^^^

.. warning::
    Removed in version 1.6.0. Keep it for the legacy subscription overview.
    For the new subscription overview use :ref:`template overrides <reference-templates-extend_subscription_overview_single>` instead.

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

.. note::
    Since Version 1.6.0 this hook shall be called with the package name (as in imports)
    as the only argument. Juntagrico will identify the installed version automatically.

Shows the given version with the given name on the version page

Arguments:

- name: String
- version: String (deprecated since juntagrico 1.6.0)
