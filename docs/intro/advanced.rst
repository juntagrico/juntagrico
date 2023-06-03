Advanced Setup
==============

Addons
------

You can install the following addons to extend the functionality of Juntagrico:

* `juntagrico-billing <https://github.com/juntagrico/juntagrico-billing>`_: create bills, send bills and manage payments.
* `juntagrico-custom-sub <https://github.com/juntagrico/juntagrico-custom-sub>`_: allow the user to select the amount of predefined products in his or her subscription.
* `juntagrico-assignment-request <https://github.com/juntagrico/juntagrico-assignment-request>`_: allow members to request assigments for jobs they have done, that were not announced.
* `juntagrico-pg <https://github.com/juntagrico/juntagrico-pg>`_: postgres database editor for admins.
* `juntagrico-badges <https://github.com/juntagrico/juntagrico-badges>`_: allows distributing virtual badges to members and group and organize them based on these.
* `juntagrico-crowdfunding <https://github.com/juntagrico/juntagrico-crowdfunding>`_: allows you to create (public) crowdfunding campaigns.
* `juntagrico-webdav <https://github.com/juntagrico/juntagrico-webdav>`_: include webdav folders in order to share files with your members.

The linked repositories contain additional information and installation instructions.


.. _intro-rich-text-editor:

Rich Text Editor
----------------

The rich text editor allows formatting text of most descriptions, like the job descriptions, entered through the admin interface,
This feature is disabled by default. Use the steps below to enable it.

.. warning::
    When the rich text editor is enabled, text, when saved, will be saved as HTML.
    Disabling the rich text editor will not convert the text back. The HTML has to be converted back manually.

.. note::
    When text from rich text fields is used in plain text emails the HTML tags need to be removed using the ``striptags`` filter.
    This is done in the default email templates. You will have to do it in your customized email texts as well.

To enable the rich text editor you have to do the following:

* Add ``'djrichtextfield'`` to your ``INSTALLED_APPS`` in the settings
* Add ``re_path(r'^djrichtextfield/', include('djrichtextfield.urls')),`` to your urls (also make sure to import ``re_path`` from ``django.urls``)
* Add the following setting
    .. code-block:: python

        DJRICHTEXTFIELD_CONFIG = {
            'js': ['/static/juntagrico/external/tinymce/tinymce.min.js'],
            'init_template': 'djrichtextfield/init/tinymce.js',
            'settings': {
                'menubar': False,
                'plugins': 'link  lists',
                'toolbar': 'undo redo | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | bullist numlist | link'
            }
        }


The example above uses the TinyMCE editor, which comes pre-installed with juntagrico. You may use any other editor.

More information on django-richtextfield you can find here https://pypi.org/project/django-richtextfield/


.. _intro-custom-templates:

Custom Templates
----------------

.. Note::
    Changing the templates will increase your maintenance work.
    If you think the changes you want to make could also benefit other juntagrico users, consider opening an issue, suggesting your changes to juntagrico directly.
    If you need your changes quickly, you may still want to override the templates as described here.

Read `the official documentation <https://docs.djangoproject.com/en/4.2/howto/overriding-templates/>`_ on how to override templates in django.

Roughly these are the steps to override a template:

1. Either ensure, that your ``INSTALLED_APPS`` are in the desired order
   or add ``DIRS`` to your ``TEMPLATES`` settings in ``{app}/settings.py``, e.g.:

.. code-block:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],  # location of your overriding templates
            'APP_DIRS': True,
            # ...
        },
    ]

2. Copy the juntagrico template that you want to override from ``juntagrico/templates``
   (in the juntagrico source code) to your ``templates`` folder (in your app or in the project root, depending on the above setting),
   while preserving the folder structure.
3. The project will now use your copy of the template instead of the original.

.. Hint::
    Some texts, e.g. of forms, do not appear in the template. To change these :ref:`see below <intro-modify-text-in-code>`


.. _intro-custom-code:

Custom Code
-----------

You can modify juntagrico through the provided :ref:`Hooks <reference-hooks>`.
You may also apply monkey patching, but be aware, that juntagrico may change in the future and you will have to maintain your changes accordingly.
It is best practise to report features that you are adding this way, to either get them included in juntagrico or at least get an official hook to do your changes.

Modifications can be made, once all django apps have been loaded,
i.e. in the ``ready`` method of your app config in ``apps.py`` in the main folder of your project or addon:

  .. code-block:: python

    from django.apps import AppConfig
    from juntagrico.util import addons

    class MyConfig(AppConfig):
        name = 'myapp'
        verbose_name = "My App"

        def ready(self):
            addons.config.register_user_menu('my_user_menu.html')
            # register other hooks
            # Add Monkey-Patches ..


.. _intro-modify-text-in-code:

Modifying Text in Code
^^^^^^^^^^^^^^^^^^^^^^

Some text is written directly into code instead of templates. These texts can be modified with :ref:`Custom Code <intro-custom-code>`.

.. code-block:: python

    def ready(self):
        # import the form to patch
        from juntagrico.forms import RegisterMemberForm
        # modify text variable (check the form implementation to see if this is available)
        RegisterMemberForm.text['accept_wo_docs']= 'I accept'
        # modify field labels of a ModelForm
        RegisterMemberForm.base_fields['phone'].label = 'Tel'
        # modify the text in a submit button
        old_init = RegisterMemberForm.__init__

        def my_init(self, *args, **kwargs):
            old_init(self, *args, **kwargs)
            self.helper.layout[-1].fields[0].value = 'Go'

        RegisterMemberForm.__init__ = my_init
