.. _reference-templates:

Templates
=========

In django templates can be overwritten and modified by other apps.

Juntagrico provides template snippets or template blocks, that allow you to modify
parts of certain templates, e.g., descriptive text or menu entries.

.. Note::
    Templates or template blocks that are not documented in this reference
    may change in future versions without notice.
    Changing undocumented and will increase your maintenance work.

    If you think the changes you want to make could also benefit other juntagrico users,
    consider opening an issue, suggesting your changes to juntagrico directly.
    If you need your changes quickly, you may still want to override the templates as described here.

.. Hint::
    Some texts, e.g. of forms, do not appear in the template. To change these :ref:`see below <intro-modify-text-in-code>`

Set up Template Overrides
-------------------------

The instructions for overriding templates in django can be found in the `the official documentation <https://docs.djangoproject.com/en/4.2/howto/overriding-templates/>`_.
Roughly these are the steps:

1. In the ``settings.py`` either enable the ``app_directories`` template loader
   or set ``APP_DIRS`` to True on the ``TEMPLATES`` setting. And make sure that the app with
   the template overrides is somewhere above ``'juntagrico'`` in the ``INSTALLED_APPS``

   Alternatively, you can set ``DIRS`` to your ``TEMPLATES`` settings to the folder where you
   will place the template overrides.

.. code-block:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,  # Option 1: This is needed for addons that override templates
            'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Option 2: location of your overriding templates
            # ...
        },
    ]

2. Create a template file in your templates folder (in your app or in the project root, depending on the above setting)
   with the same path as the
   `template file in juntagrico <https://github.com/juntagrico/juntagrico/tree/main/juntagrico/templates>`_,
   that you want to override.
3. The project will now use your copy of the template instead of the original.
   If you only want to modify certain blocks on that template, extend the original template and
   modify the block(s) like this:

.. code-block:: html

    {% extends "path/to/this/template.html" %}
    {% block block_to_override %}
        {{ block.super }} {#% insert the original content of this block, if you want %#}
        {#% add your own block content %#}
    {% endblock %}


Menu Templates
--------------

.. Note::

    Make sure to always add ``{{ block.super }}`` to include extensions by addons.

.. _reference-templates-extend_user_menu:

juntagrico/menu/user.html|extend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add entries to the user menu.

Example:

.. code-block:: html

    {% extends 'juntagrico/menu/user.html' %}
    {% block extend %}
        {% include 'your/own/admin_menu.html' %}
        {{ block.super }}
    {% endblock %}


.. _reference-templates-extend_admin_menu:

juntagrico/menu/admin.html|extend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add entries to the admin menu.

Example:

.. code-block:: html

    {% extends 'juntagrico/menu/admin.html' %}
    {% block extend %}
        {% include 'your/own/admin_menu.html' %}
        {{ block.super }}
    {% endblock %}


.. _reference-templates-extend_admin_subscription_menu:

juntagrico/menu/admin/subscriptions.html|extend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add entries to the subscription section in the admin menu.


.. _reference-templates-extend_subscription_overview_single:

juntagrico/my/subscription/single.html|extend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add content to the subscription overview page, for members that have a subscription.


.. _reference-templates-extend_subscription_overview_none:

juntagrico/my/subscription/none.html|extend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add content to the subscription overview page, for members that have no subscription.
