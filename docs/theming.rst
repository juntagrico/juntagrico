Theming
=======

Custom CSS
----------

1. Add your custom CSS file e.g. ``{app}/static/css/{app}.css``
2. Adjust the ``STYLE_SHEET`` setting to point to that file

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
