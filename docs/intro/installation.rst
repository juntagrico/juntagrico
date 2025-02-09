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
If you used the cookiecutter template, above this settings will already be set.
Otherwise refer to the `demo application settings <https://github.com/juntagrico/juntagrico-demo/blob/main/demo/settings.py>`_.

Hook URLs in URLconf
--------------------

Add the juntagrico urls to you urls.py e.g.:

.. code-block:: python

    # urls.py
    from django.urls import path, include
    from django.contrib import admin

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('impersonate/', include('impersonate.urls')),
        path('', include('juntagrico.urls')),
    ]


.. _intro-initial-django-setup:

Initial Django setup
--------------------

Use the django commands to set up the database:

.. code-block:: bash

    $ python -m manage migrate

In production (``DEBUG=False``) the static files must be collected:

.. code-block:: bash

    $ python -m manage collectstatic

Create a superuser with member to login into your instance:

.. code-block:: bash

    $ python -m manage createadmin


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
