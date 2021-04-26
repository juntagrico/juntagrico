Rich Text Editor
================

Overview
--------

juntagrico now ships with the django app django-richtextfield which is not enabled by default.
If you want to enable a rich text editor for the textfields in your administration area you
have to follow the steps below.

If you want more information on django-richtextfield you can find it here https://pypi.org/project/django-richtextfield/

Installation
------------
To enable the rich text editor you have to do the following:

* Add ``'djrichtextfield'`` to your ``INSTALLED_APPS`` in the settings
* Add ``re_path(r'^djrichtextfield/', include('djrichtextfield.urls')),`` to your urls (also make sure to import ``re_path`` from ``django.urls``)
* Add the following setting
    .. code-block:: python

        DJRICHTEXTFIELD_CONFIG = {
            'js': ['/static/external/tinymce/tinymce.min.js'],
            'init_template': 'djrichtextfield/init/tinymce.js',
            'settings': {
                'menubar': False,
                'plugins': 'link  lists',
                'toolbar': 'undo redo | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | bullist numlist | link'
            }
        }

Choose Your Own Rich Text Editor Implementation
-----------------------------------------------
django-richtextfield allows for a variety of different rich text editor implementations. The code above for the
``DJRICHTEXTFIELD_CONFIG`` setting just makes use of the TinyMCE shipped with juntagrico but you can choose whatever you want.

Custom Mail Templates
---------------------
Since juntagrico sends plaintext emails the raw content of a rich text field would be displayed which is html content.
Because raw html is not very user-friendly to read we apply the ``striptag`` filter in the default email texts for possible rich text fields.
If you override one of these templates and use a rich text editor you should do the same in your custom templates.

Disabling the Rich Text Editor
------------------------------
Disabling the rich text editor will not convert back the texts to non html. This has to be done manually.