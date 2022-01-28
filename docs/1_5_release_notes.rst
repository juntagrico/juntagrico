Release Notes
=============

1.5.0
-----

Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^
* Configure the website name and domain as specified in the :doc:`First Steps <first_steps>`
  using the values from your ``ADMINPORTAL_NAME`` and ``ADMINPORTAL_SERVER_URL`` settings.
    * Remove these settings.
    * Add ``'django.contrib.sites.middleware.CurrentSiteMiddleware'`` to the ``MIDDLEWARE`` setting.
* Replace the ``STYLE_SHEET`` setting with ``STYLES = {'static': ['your.css']}``
* Add the Setting STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

Fixes
^^^^^

Features & Improvements
^^^^^^^^^^^^^^^^^^^^^^^
* Member Features:

* Admin Features:
    * Members have now a field number in the data administration
    * Edit pages of jobs, areas and depots now show a link to the frontend of the edited element on the top right
    * Uploaded email attachments can now be removed
    * Activity areas can be flagge to be added automatically to a member on creation
    * depot description is now optional
    * price is now a decimal value

* Developer Features:
    * ``ADMINPORTAL_NAME`` and ``ADMINPORTAL_SERVER_URL`` are removed in favor of the sites app. See upgrade instructions.
    * Added settings ``SCRIPTS`` and ``STYLES`` and removed ``STYLE_SHEET``
    * The mailer textfield can now be configured using the new `MAILER_RICHTEXT_OPTIONS` setting
    * Enable use of setting STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'



