Theming
=======

Custom CSS
----------

1. Add your custom CSS file e.g. ``{app}/static/css/{app}.css``
2. Adjust the ``STYLES`` setting to point to that file: ``STYLES = {'static': ['css/{app}.css']}``

Note that the setting is specified without the ``{app}`` folder,
as django will collect all static files into a single location.

Change the Logo
---------------
In the custom CSS set your logo as the background image of the ``.juntagrico_logo`` element. e.g.:

.. code-block:: css

    .juntagrico_logo {
        background: url(/static/img/logo-{app}.png) center center;
        background-size: contain;
        background-repeat: no-repeat;
        display: inline-block;
        width: 300px;
        height: 300px;
    }

Then add the image file to ``{app}/static/img/logo-{app}.png`` or as specified in the css before.

Custom Templates
----------------

Note: Changing the templates will increase your maintenance work.
If you think the changes you want to make could also benefit other juntagrico users, consider opening an issue, suggesting your changes to juntagrico directly.
If you need your changes quickly, you may still want to override the templates as described here.

1. In the ``TEMPLATES`` entry in your ``{app}/settings.py`` add the filesystem loader and specify ``DIRS``:

.. code-block:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],  # location of your overriding templates
            'OPTIONS': {
                # ...
                'loaders': [
                    'django.template.loaders.filesystem.Loader',  # use filesystem loader first
                    'django.template.loaders.app_directories.Loader'
                ],
            },
        },
    ]

2. Create a ``templates`` folder in the root of your project.
3. Copy the juntagrico template that you want to override from ``juntagrico/templates`` (in the juntagrico source code) to your new ``templates`` folder, while preserving the folder structure.
4. The project will now use your copy of the template instead of the original.
