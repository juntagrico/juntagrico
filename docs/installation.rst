Installation
============

Basic Installation
------------------
Install juntagrico with :command:`pip`:

    $ pip install juntagrico


Django Settings
---------------
The following django settings are necessary to run juntagrico.

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
        'adminsortable2',
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
    ]
    
Since we use session we need a serializer

.. code-block:: python

    SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
    
Django also needs to be configured to send emails and to access a database. If you need more helping points see the testsettings in the project folder


juntagrico Settings
--------------------
For more information see the settings page.
