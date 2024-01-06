.. _intro-installation:

Installation
============

.. note:: If your instance runs on the hosted Juntagrico PaaS this installation is done for you.
    Continue with the :ref:`basic setup <intro-basic-setup>`.


Installation using Cookie Cutter
--------------------------------
You may use the `cookiecutter template <https://github.com/juntagrico/juntagrico-science-django-cookiecutter>`_ to create your app.
This will create an app, with all the required settings set as described in the manual installation.
See `Cookiecutter <https://pypi.org/project/cookiecutter/>`_ for usage.

Then install the requirements with :command:`pip`:

.. code-block:: bash

    $ pip install -r requirements.txt

Further the database and email connection need to be configured using environment variables or directly in the `settings.py`. Refer to the generated `settings.py` and the django documentation.

Continue with :ref:`Initial Django setup <intro-initial-django-setup>`.

Manual Installation
-------------------
Juntagrico is an reusable django app. You should create your own django app and install juntagrico as an app (see below).

See the `demo app <https://github.com/juntagrico/juntagrico-demo>`_ for reference.

Juntagrico can be installed via :command:`pip`:

.. code-block:: bash

    $ pip install juntagrico


Django Settings
---------------
The following django settings are necessary to run juntagrico. If you used the cookiecutter template, above this settings will already be set.

Additional to juntagrico the following apps have to installed into django:

.. code-block:: python

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'juntagrico',
        'impersonate',
        'crispy_forms',
        'adminsortable2',
        'demo',
        'polymorphic',
    ]
    
The following authentication settings are required

.. code-block:: python

    AUTHENTICATION_BACKENDS = (
        'juntagrico.util.auth.AuthenticateWithEmail',
        'django.contrib.auth.backends.ModelBackend'
    )
    
Additionally also some changes in the middleware have to to be added

.. code-block:: python

    MIDDLEWARE = [
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'impersonate.middleware.ImpersonateMiddleware',
        'django.contrib.sites.middleware.CurrentSiteMiddleware',
    ]
    
Since we use session we need a serializer

.. code-block:: python

    SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

Further settings need to be configured to send emails and to access a database.
If you need more helping points see the testsettings in the juntagrico project folder or refer to the `demo application settings <https://github.com/juntagrico/juntagrico-demo/blob/main/demo/settings.py>`_.


Hook URLs in URLconf
--------------------

Add the juntagrico urls to you urls.py e.g.:

.. code-block:: python

    # urls.py
    from django.contrib import admin
    from django.urls import path
    import juntagrico

    urlpatterns = [
        path(r'impersonate/', include('impersonate.urls')),
        path(r'', include('juntagrico.urls')),
        path(r'', juntagrico.views.home),
    ]


.. _intro-initial-django-setup:

Initial Django setup
--------------------

Use the django commands to set up the database e.g.:

.. code-block:: bash

    $ python -m manage migrate

In production (``DEBUG=False``) the static files must be collected e.g.:

.. code-block:: bash

    $ python -m manage collectstatic

Create a superuser to login into your instance. e.g.:

.. code-block:: bash

    $ python -m manage createsuperuser

For juntagrico a member needs to be created for the super user using

.. code-block:: bash

    $ python -m manage create_member_for_superusers

Create Test Data (optional)
---------------------------

If you want to test juntagrico, these commands will populate your new instance with some example data. Do not do this in production!

Simple example data

.. code-block:: bash

    $ python -m manage generate_testdata

More complex example data

.. code-block:: bash

    $ python -m manage generate_testdata_advanced

Run the Server
--------------

You should now be able to start the django server and open the instance in the browser e.g.:

.. code-block:: bash

    $ python -m manage runserver
