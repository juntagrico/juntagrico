Addons
======

Juntagrico is a django app and can be extended with additional django apps.
This page lists the various ways in which such addons can integrate with juntagrico.

For a list of existing addons :ref:`See Advanced Setup <intro-addons>`.

Override Templates
------------------

Templates can be overridden by the addon in the same way the project can override templates.
Addons must be added **above** juntagrico in the ``INSTALLED_APPS``.
:ref:`See Templates Reference <reference-templates>`.

Extend Signup
-------------

Add a page to the signup process
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Add a url and view for your new signup page.
2. Subclass the signup manager class and instruct the user to set it in
   the :ref:`SIGNUP_MANAGER <settings-signup-manager>` setting.
3. In your new signup view, when the form is submitted successfully,
   save the data in your signup manager or at least save a flag there,
   that the step was completed. Note that the session must be JSON serializable.
4. Override the ``get_next_page`` method of your signup manager and
   define the criteria, when the new page should be loaded. E.g., when
   the depot has been selected, but your new entity hasn’t.
   Return the url name of your new page in that case.

Modify the summary page
^^^^^^^^^^^^^^^^^^^^^^^

1. Override an adjacent block in the summary page template to add your new entity.
2. Create an edit link in your summary section, that leads back to the
   new page of the signup process and allows modifying the selection.

Save and notify
^^^^^^^^^^^^^^^

1. Override the ``apply`` method or one of the specific ``apply_...``
   methods of your custom signup manager. E.g. if you need the
   subscription to be saved before your new entity can be saved,
   override ``apply_subscriptions``, call the super method and then save
   your new entity.
2. Send emails notifications if needed. Either in the same place or
   overriding the ``send_emails`` method.
