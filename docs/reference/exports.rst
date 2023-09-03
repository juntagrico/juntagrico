.. _reference-exports:

Exports
=======

Juntagrico uses `django_import_export <https://django-import-export.readthedocs.io/en/stable/>`_ to provide customizable data exports.

Add Export
----------

Exports are defined in a ``Resource`` class.
Read the `documentation of django_import_export on how to define resources <https://django-import-export.readthedocs.io/en/stable/advanced_usage.html#customize-resource-options>`.

Example Resources
^^^^^^^^^^^^^^^^^

.. code-block:: python

    from import_export import resources

    class MyDepotResource(resources.ModelResource):
        class Meta:
            model = Depot
            name = 'My Depot Resource'


    class MyShareResource(resources.ModelResource):
        class Meta:
            model = Share
            name = 'My Share Resource'



Integrating your Resources
^^^^^^^^^^^^^^^^^^^^^^^^^^

You need to modify the admin classes, where the export shall be shown. See :ref:`Custom Code <intro-custom-code>` on where to add this code.

If the admin already has an export, it is easy to add another one:

.. code-block:: python

    from juntagrico.admins.share_admin import ShareAdmin
    from juntagrico.resources import MyShareResource
    ShareAdmin.resource_classes.append(MyShareResource)

Otherwise you will have to modify the existing admin with the ``ExportMixin`` class.

.. note::
    For admins that use the ``SortableAdminMixin``, use ``SortableExportMixin`` instead.

.. code-block:: python

        from juntagrico.admins import SortableExportMixin
        from juntagrico.admins.depot_admin import DepotAdmin
        from juntagrico.resources import MyDepotResource
        from django.contrib import admin
        from juntagrico.entity.depot import Depot

        # Extend the existing admin class
        class ExportableDepotAdmin(SortableExportMixin, DepotAdmin):
            resource_classes = [MyDepotResource]

        # replace previously registered admin
        admin.site.unregister(Depot)
        admin.site.register(Depot, ExportableDepotAdmin)
