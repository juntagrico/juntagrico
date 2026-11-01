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
They set the headers ``X-Frame-Options: DENY`` and ``X-Content-Type-Options: nosniff``.
Also set the referrer policy as in ``settings/minimal.py``:

.. code-block:: python

    # settings.py
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

Do not keep the django default ``same-origin``: with it, browsers send no ``Referer`` header to other sites.
The OpenStreetMap tile servers then block the tiles of the depot maps,
and external services such as web analytics may reject the requests.
Ideally, these headers are set by the web server in front of django instead,
so that they also apply to responses not served by django, such as static and media files
(see the `django documentation <https://docs.djangoproject.com/en/5.2/ref/middleware/#module-django.middleware.security>`_).
In that case make sure the headers are not sent twice with conflicting values,
and use the same referrer policy in the web server.
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
