.. _intro-deployment:

Deployment
==========

Security in production
----------------------

Run the django deployment checks against your production settings and resolve the warnings:

.. code-block:: bash

    $ python -m manage check --deploy

In particular, enable the security and clickjacking middlewares as in
`settings/minimal.py <https://github.com/juntagrico/juntagrico/blob/main/settings/minimal.py>`_.
With the django defaults they set the headers ``X-Frame-Options: DENY``, ``X-Content-Type-Options: nosniff``
and ``Referrer-Policy: same-origin``.
Ideally, these headers are set by the web server in front of django instead,
so that they also apply to responses not served by django, such as static and media files
(see the `django documentation <https://docs.djangoproject.com/en/5.2/ref/middleware/#module-django.middleware.security>`_).
In that case make sure the headers are not sent twice with conflicting values.
If your instance is only reachable via HTTPS, also mark the cookies as secure:

.. code-block:: python

    # settings.py
    if not DEBUG:
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True

``Strict-Transport-Security`` (HSTS) can be set either with ``SECURE_HSTS_SECONDS`` or in the web server in front of django.
If django runs behind a proxy, ``SECURE_SSL_REDIRECT`` requires ``SECURE_PROXY_SSL_HEADER`` and a proxy that sets this header,
otherwise the redirect loops.
Refer to the `django deployment checklist <https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/>`_ for details.

.. _intro-security:

Security Hardening
------------------

Juntagrico provides several security hardening measures described below.

.. _intro-security-password:

Password Validation
^^^^^^^^^^^^^^^^^^^

Juntagrico now supports role-based password validation. When a user logs in with
a password that does not meet the configured requirements, a middleware will
restrict their session to the password change page until they set a stronger
password.

To enable, add the middleware and configure password validators in your
``settings.py``:

.. code-block:: python

    MIDDLEWARE = [
        # ...
        'juntagrico.middleware.RequirePasswordChangeMiddleware',
        # ...
    ]

    from juntagrico.defaults import password_validators

    AUTH_PASSWORD_VALIDATORS = password_validators

The recommended default validators (from ``juntagrico.defaults.password_validators``)
enforce a minimum length of 12 characters, check against common passwords, and
prevent passwords that resemble the user's personal information (name, email,
address, phone number, birthday).

**Role-based validators.** Juntagrico provides specialized validators that apply
strict rules only to users with elevated privileges:

- ``StaffOnlyPasswordValidator`` — applies the wrapped validators to staff and
  superusers only.
- ``PermittedOnlyPasswordValidator`` — extends the above to users who have any
  permissions or group memberships.
- ``PrivilegedOnlyPasswordValidator`` — further extends to users who coordinate
  activity areas or depots.
- ``GroupOnlyPasswordValidator`` — applies validators only to members of a
  specific group (default: ``'NeedsStrongPassword'``).

Example — require strong passwords for staff and coordinators:

.. code-block:: python

    from juntagrico.password_validation import PrivilegedOnlyPasswordValidator

    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': PrivilegedOnlyPasswordValidator,
            'VALIDATORS': [
                {
                    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
                    'OPTIONS': {'min_length': 16},
                },
                {
                    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
                },
            ],
        },
        # fallback validators for all users
        *password_validators,
    ]

.. note::
    The ``RequirePasswordChangeMiddleware`` allows certain URLs to remain
    accessible even during the forced password change flow. By default these are
    the password page, logout, JS i18n, and impersonate-stop. You can extend
    this list with the :ref:`ALWAYS_ALLOWED_URLNAMES <reference-settings-always-allowed-urlnames>` setting.

Rich Text Sanitization
^^^^^^^^^^^^^^^^^^^^^^

When the rich text editor is enabled in the admin interface, all HTML content
saved through it is automatically sanitized using the ``nh3`` library. Only a
whitelist of safe tags (``<p>``, ``<strong>``, ``<em>``, ``<a>``, lists, etc.)
and attributes (``href``, ``title``, ``target`` on links; ``style`` everywhere)
are preserved. Dangerous constructs like ``<script>`` tags and event handlers
(e.g. ``onclick``) are stripped.

The sanitizer is configured via the ``sanitizer_profiles`` key in
``DJRICHTEXTFIELD_CONFIG``, which is set automatically when you use
``defaults.richtextfield_config()``.

**Cleaning existing data.** If you already have HTML content in your database
that was entered before sanitization was enabled, run the
:ref:`sanitize_richtext <reference-commands-sanitize-richtext>` management
command to clean it:

.. code-block:: bash

  python manage.py sanitize_richtext --dry-run
  python manage.py sanitize_richtext

Open Redirect Protection
^^^^^^^^^^^^^^^^^^^^^^^^

All redirect URLs — including the ``next`` parameter in the Django admin and
the referer-based return-after-action redirects — are now validated. Only URLs
that resolve to a known route in the application are followed; external or
invalid URLs are safely ignored, and the user is redirected to the home page
instead.

Optional Impersonation
^^^^^^^^^^^^^^^^^^^^^^

The ``impersonate`` third-party app is now optional. If it is not listed in
``INSTALLED_APPS``, the impersonation-related UI elements are simply hidden,
and the application runs without errors.

If you do use impersonation, you can restrict who may impersonate other users
using the helpers in ``juntagrico.defaults``:

.. code-block:: python

    IMPERSONATE = {
        'CUSTOM_ALLOW': 'juntagrico.defaults.allow_group',
        'CUSTOM_USER_QUERYSET': 'juntagrico.defaults.unprivileged_only',
    }

The ``CUSTOM_ALLOW`` value should be a dotted path to a callable, for example
``'juntagrico.defaults.allow_group'`` configured with an `'impersonators'`` group.
Similarly, ``CUSTOM_USER_QUERYSET`` should be a string like
``'juntagrico.defaults.unprivileged_only'``.

Available queryset presets:

- ``nonstaff_only`` — all users except staff and superusers.
- ``nonpermitted_only`` — users without any permissions or group memberships.
- ``unprivileged_only`` — users without permissions, groups, or coordination
  roles (activity areas or depots).

For maximum security, you may also limit impersonation to superusers only:

.. code-block:: python

    IMPERSONATE = {
        'REQUIRE_SUPERUSER': True,
    }

Mail Template Locking
^^^^^^^^^^^^^^^^^^^^^

By default, mail templates are read-only in the admin interface to prevent
unauthorized modification of email content. Set
:ref:`UNLOCK_MAILTEMPLATES <reference-settings-unlock-mailtemplates>` to
``True`` in your settings to re-enable editing.
