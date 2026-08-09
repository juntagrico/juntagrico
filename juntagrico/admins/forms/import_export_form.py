import datetime

from django import forms
from django.db.models import Max, Min
from django.forms import SelectDateWidget
from django.utils.translation import gettext as _

from import_export.forms import SelectableFieldsExportForm

from juntagrico.entity.jobs import Job
from juntagrico.util.temporal import start_of_business_year, end_of_business_year


class TranslatedSelectableFieldsExportForm(SelectableFieldsExportForm):
    def _get_field_label(self, resource, field_name):
        field = resource.fields.get(field_name)
        if field and hasattr(resource, 'verbose_names'):
            if verbose_name := resource.verbose_names().get(field.column_name):
                return f"{verbose_name} ({field.column_name})"
        return field_name.replace("_", " ").title()


class ExportAssignmentDateRangeForm(TranslatedSelectableFieldsExportForm):
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
        this_year = datetime.date.today().year
        # extend range to year before and after to be able to always select entire business year.
        years = range(
            (jobs['oldest_year'] or this_year) - 1,
            (jobs['newest_year'] or this_year) + 2,
        )
        self.fields['export_start_date'].widget.years = years
        self.fields['export_end_date'].widget.years = years
