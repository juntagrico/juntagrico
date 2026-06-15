

class DateRangeResourceMixin:
    """
    Use in combination with DateRangeExportMixin on admin.
    collects the selected date range and makes it available in the resource.
    """
    def __init__(self, start_date=None, end_date=None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
