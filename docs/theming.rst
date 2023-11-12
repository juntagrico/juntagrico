Theming
=======

Custom CSS
----------

If you create a new project, a custom css file is already installed.
Otherwise you can install a custom css file using these steps:

1. Add your custom CSS file e.g. ``{app}/static/{app}/css/customize.css``
2. Adjust the ``STYLES`` setting to point to that file: ``STYLES = {'static': ['{app}/css/customize.css']}``

Note that the setting is specified without the ``{app}/static/`` part in the path.

Change the Logo
---------------

1. In the custom CSS set your logo as the background image of the ``.juntagrico_logo`` element. e.g.:

.. code-block:: css

    .juntagrico_logo {
        background: url(/static/{app}/img/logo.png) center center;
        background-size: contain;
        background-repeat: no-repeat;
        display: inline-block;
        width: 300px;
        height: 300px;
    }

2. add the image file to ``{app}/static/{app}/img/logo.png`` as specified in the css before.

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
