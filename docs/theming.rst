Theming
=======

Custom CSS
----------
Add your custom CSS file e.g. ``{app}/static/css/personal.css``

When using a filename other than the above, you will have to adjust the ``STYLE_SHEET`` setting.
Note that the setting is specified without the ``{app}`` folder,
as django will collect all static files into a single location.

Change the Logo
---------------
In the custom CSS set your logo as the background image of the ``.juntagrico_logo`` element. e.g.:

.. code-block:: css

    .juntagrico_logo {
        background: url(/static/img/logo.png) center center;
        background-size: contain;
        background-repeat: no-repeat;
        display: inline-block;
        width: 300px;
        height: 300px;
    }

Then add the image file to ``{app}/static/img/logo.png`` or as specified in the css before.
