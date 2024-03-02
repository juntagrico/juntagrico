from import_export import resources


class ModQuerysetModelResource(resources.ModelResource):
    """
    ModelResource with modifiable queryset
    """
    def update_queryset(self, queryset):
        return queryset

    def get_queryset(self):
        return self.update_queryset(super().get_queryset())

    def export(self, queryset=None, *args, **kwargs):
        if queryset is not None:
            queryset = self.update_queryset(queryset)
        return super().export(queryset, *args, **kwargs)


class DateRangeResourceMixin:
    """
    Use in combination with DateRangeExportMixin on admin.
    collects the selected date range and makes it available in the resource.
    """
    def __init__(self, start_date=None, end_date=None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
