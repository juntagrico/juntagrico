.. _intro-installation:

Installation
============

.. note:: If your instance runs on the hosted Juntagrico PaaS this installation is done for you.
    Continue with the :ref:`basic setup <intro-basic-setup>`.


Prerequisites
-------------

Make sure `python <https://www.python.org/>`_ is installed on your system.


Create new Django app using Cookiecutter
----------------------------------------
You may use the `cookiecutter template <https://github.com/juntagrico/juntagrico-science-django-cookiecutter>`_
to create a fresh django app.
This will create a django project and app, with all the required settings and urls set up.

.. code-block:: bash

    $ pip install cookiecutter
    $ cookiecutter gh:juntagrico/juntagrico-science-django-cookiecutter

Check out the `Cookiecutter documentation <https://pypi.org/project/cookiecutter/>`_ on how to install cookiecutter on your system.

Then install the requirements with :command:`pip`:

.. code-block:: bash

    $ pip install -r requirements.txt

The default setup will use a local SQLite database and fails to send out emails.
For production you will need to configure the database and email connection using environment variables or directly in the `settings.py`.
Refer to the generated `settings.py` and the django documentation.

You are now ready to continue with :ref:`Initial Django setup <intro-initial-django-setup>`.


Alternative: Install in an existing Django app
----------------------------------------------
If instead you already have a django project you can add juntagrico as an app to it.

Install juntagrico, e.g. via :command:`pip`:

.. code-block:: bash

    $ pip install juntagrico


Update Django Settings
^^^^^^^^^^^^^^^^^^^^^^

Update your projects ``settings.py``.

Refer to `settings/minimal.py <https://github.com/juntagrico/juntagrico/blob/main/settings/minimal.py>`_
for the minimal settings required to run Juntagrico.

For sending out emails, the corresponding django settings need to be configured properly.
Read the `django documentation <https://docs.djangoproject.com/en/4.2/ref/settings/#email-backend>`_ for more details.

In the `demo app <https://github.com/juntagrico/juntagrico-demo/blob/main/demo/settings.py>`_ you can find a
more complete set of settings, suitable for the production environment.

Additional settings will be explained in the :ref:`basic setup <intro-basic-setup>` section.

Hook URLs in URLconf
^^^^^^^^^^^^^^^^^^^^

Include these urls to your ``urls.py``:

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
