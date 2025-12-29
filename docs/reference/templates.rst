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


Email Templates
---------------

Email Templates can be overridden in the same way as every other template.
Read the :ref:`Notification reference <reference-notifications>` to see which email templates exist.

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

juntagrico/menu/admin/\*.html|sub
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change admin sub menu entries of:

- ``activityareas.html``
- ``assignments.html``
- ``depots.html``
- ``extra_subscriptions.html``
- ``lists.html``
- ``members.html``
- ``shares.html``
- ``subscriptions.html``

Signup Templates
----------------

All signup pages have these 2 blocks to override:

- ``title``: Text of the title
- ``intro``: Text after the title

The signup templates are located in the folder ``createsubscription``.

Some pages have additional blocks listed below.

signup.html
^^^^^^^^^^^

- ``intro_1``: First part of intro
- ``intro_with_shares``: Part of intro, about shares
- ``intro_2``  Last part of intro
- ``read_instructions``: Text on documents that should be read

juntagrico/form/layout/category_container.html
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Defines the structure to display subscription categories in the subscription/part order and change forms

Blocks:

- ``head``: Name and description of category
- ``fields``: Nested fields


juntagrico/form/layout/bundle_container.html
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Defines the structure to display subscription bundles in the subscription/part order and change forms.

Has the same blocks as ``category_container.html``.


juntagrico/subscription/create/form/no_subscription_field.html
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``description``: Textlabel on signup option without subscription
- ``base_fee``: Base fee description on signup option without subscription


select_depot.html|label
^^^^^^^^^^^^^^^^^^^^^^^

Labeltext of depot selection field

select_start_date.html
^^^^^^^^^^^^^^^^^^^^^^

- ``label``: Label of date selection field
- ``hint``: text below selection field

select_shares.html
^^^^^^^^^^^^^^^^^^^^^^

- ``intro_1``: First part of intro
- ``intro_2``  Last part of intro

summary.html
^^^^^^^^^^^^

Each section has a block:

- ``profile``
- ``subscription``
- ``depot``
- ``start_date``
- ``co_member``
- ``activity_areas``
- ``shares``:
- ``comment``:

Subscription Templates
----------------------

.. _reference-templates-extend_subscription_overview_single:

juntagrico/my/subscription/single.html|extend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add content to the subscription overview page, for members that have a subscription.


.. _reference-templates-extend_subscription_overview_none:

juntagrico/my/subscription/none.html|extend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add content to the subscription overview page, for members that have no subscription.


Depot Templates
---------------

depot.html
^^^^^^^^^^

Each section has a block to overwrite or extend it:

- ``address``
- ``pickup``
- ``contact``
- ``description``
- ``access_information``
- ``map``


Activity Area Templates
-----------------------

juntagrico/my/area/snippets/intro.html|all
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Override the intro text on the activity area overview page


Membership Templates
--------------------

cancelmembership.html|intro
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Text after title

profile.html
^^^^^^^^^^^^

Blocks exist for the text in the info banner on top and for the buttons

- ``info_canceled``
- ``info_active``
- ``button_change_password``
- ``button_cancel_membership``


Widget Templates
----------------

juntagrico/widgets/assignment_progress.html|progress
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change appearance of the assignment progress widget in menu.

E.g. to use the bean icon indicators of previous juntagrico versions do:

.. code-block:: html

    {% extends 'juntagrico/widgets/assignment_progress.html' %}
    {% load juntagrico.widgets %}
    {% block progress %}
        {% assignment_progress request.user.member future=False as assignments %}
        {% include "./assignment_progress/classic.html" %}
    {% endblock %}

The ``future`` argument on ``assignment_progress`` specifies if planned future assignments are counted as well:

* None: Count future assignments
* False: Don't count future assignments
* True: Count future assignments separately. This is not supported by the classic assignments widget.
