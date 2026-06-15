from django.utils.translation import gettext_lazy as _
from import_export import resources


class DateRangeResourceMixin:
    """
    Use in combination with DateRangeExportMixin on admin.
    collects the selected date range and makes it available in the resource.
    """
    def __init__(self, start_date=None, end_date=None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date


class TranslatedModelResource(resources.ModelResource):
    @classmethod
    def verbose_names(cls):
        if not hasattr(cls, '_verbose_names'):
            cls._verbose_names = {i.name: i.verbose_name for i in cls._meta.model._meta.fields}
            if hasattr(cls._meta, 'verbose_names'):
                cls._verbose_names |= cls._meta.verbose_names
        return cls._verbose_names

    def get_export_headers(self, selected_fields=None):
        return [
            self.verbose_names().get(i.split("__")[0], i)
            for i in super().get_export_headers(selected_fields)
        ]

    @classmethod
    def get_display_name(cls):
        return super().get_display_name() + ' (' + _('Übersetzt') + ')'
