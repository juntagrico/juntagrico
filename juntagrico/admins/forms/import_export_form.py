from django import forms
from django.db.models import Max, Min
from django.forms import SelectDateWidget
from django.utils.translation import gettext as _

from import_export.forms import SelectableFieldsExportForm

from juntagrico.entity.jobs import Job
from juntagrico.util.temporal import start_of_business_year, end_of_business_year


class ExportAssignmentDateRangeForm(SelectableFieldsExportForm):
    export_start_date = forms.DateField(
        label=_('Startdatum'),
        help_text=_('Startdatum für Einsatzzählung'),
        widget=SelectDateWidget,
        initial=start_of_business_year
    )

    export_end_date = forms.DateField(
        label=_('Enddatum'),
        help_text=_('Enddatum für Einsatzzählung'),
        widget=SelectDateWidget,
        initial=end_of_business_year
    )

    def __init__(self, formats, *args, **kwargs):
        super().__init__(formats, *args, **kwargs)
        # offer meaningful year range
        jobs = Job.objects.aggregate(oldest_year=Min('time__year'), newest_year=Max('time__year'))
        years = range(jobs['oldest_year'], jobs['newest_year'] + 1)
        self.fields['export_start_date'].widget.years = years
        self.fields['export_end_date'].widget.years = years
