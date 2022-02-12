Release Notes
=============

Dev
---

Fixes
^^^^^
* Fix datepicker in management lists

1.5.0
-----

Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^
* Configure the website name and domain as specified in the :doc:`First Steps <first_steps>`
  using the values from your ``ADMINPORTAL_NAME`` and ``ADMINPORTAL_SERVER_URL`` settings.
    * Remove these settings.
    * Add ``'django.contrib.sites.middleware.CurrentSiteMiddleware'`` to the ``MIDDLEWARE`` setting.
* Add ``'polymorphic'`` to the ``INSTALLED_APPS`` setting.
* Replace the ``STYLE_SHEET`` setting with ``STYLES = {'static': ['your.css']}``
* The method ``url`` from ``django.conf.urls`` use either ``path`` or ``repath`` from ``django.urls``
* Add the Setting ``STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'``
* The option ``Telefonnummer von KoordinatorIn anzeigen`` on activity areas was previously only used to show the
  phone number of the area coordinator in job reminder emails and has been removed.
  Use to new contact field to show a phone number consistently in all places where the area contact is displayed.

Fixes
^^^^^
* Fix shares overview for members that have no shares this year

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* Member Features:

* Admin Features:
    * Edit pages of jobs, areas and depots now show a link to the frontend of the edited element on the top right
    * Uploaded email attachments can now be removed
    * Activity areas can be flagged to be added automatically to a member on creation
    * depot description is now optional
    * price is now a decimal value
    * Areas, jobs and job types can now have a list of contacts

* Developer Features:
    * ``ADMINPORTAL_NAME`` and ``ADMINPORTAL_SERVER_URL`` are removed in favor of the sites app. See upgrade instructions.
    * Added settings ``SCRIPTS`` and ``STYLES`` and removed ``STYLE_SHEET``
    * The mailer textfield can now be configured using the new `MAILER_RICHTEXT_OPTIONS` setting
    * Enable use of setting STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'




