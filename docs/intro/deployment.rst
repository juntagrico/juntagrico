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
