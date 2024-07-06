from django.conf import settings
from django.contrib import admin
from django.db.models import TextField
from djrichtextfield.widgets import RichTextWidget
from import_export.admin import ExportMixin

from juntagrico.admins.forms.import_export_form import ExportAssignmentDateRangeForm
from juntagrico.util import addons


class BaseAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        self.inlines = self.inlines or []
        self.inlines.extend(addons.config.get_model_inlines(model))
        super().__init__(model, admin_site)


class RichTextAdmin(BaseAdmin):

    def __init__(self, model, admin_site):
        if 'djrichtextfield' in settings.INSTALLED_APPS and hasattr(settings, 'DJRICHTEXTFIELD_CONFIG'):
            self.formfield_overrides = self.formfield_overrides or {}
            self.formfield_overrides.update({TextField: {'widget': RichTextWidget}})
        super().__init__(model, admin_site)


class OverrideFieldQuerySetMixin:
    def get_form(self, request, obj=None, **kwds):
        form = super().get_form(request, obj, **kwds)
        for field in form.base_fields:
            if hasattr(self, f"get_{field}_queryset"):
                form.base_fields[field].queryset = getattr(self, f"get_{field}_queryset")(request, obj)
        return form


class DateRangeExportMixin(ExportMixin):
    """
    Adds selection of a date range when exporting.
    Use in combination with DateRangeResourceMixin.
    """
    export_form_class = ExportAssignmentDateRangeForm

    def get_data_for_export(self, request, queryset, *args, **kwargs):
        return super().get_data_for_export(request, queryset, *args, form=kwargs.get('export_form'), **kwargs)

    def get_export_resource_kwargs(self, request, *args, **kwargs):
        form = kwargs.pop('form')
        return dict(
            start_date=form.cleaned_data['start_date'],
            end_date=form.cleaned_data['end_date'],
        )

    def get_export_filename(self, request, queryset, file_format):
        # add date range to filename
        ext = file_format.get_extension()
        start_date = request.POST.get('start_date_year') + '-' + request.POST.get('start_date_month') + '-' + request.POST.get('start_date_day')
        end_date = request.POST.get('end_date_year') + '-' + request.POST.get('end_date_month') + '-' + request.POST.get('end_date_day')
        return f'{super().get_export_filename(request, queryset, file_format)[:-len(ext)-1]}--{start_date}--{end_date}.{ext}'


class SortableExportMixin(ExportMixin):
    """ Fix to make import-export and sortable admin work together.
    """
    change_list_template = 'adminsortable2/change_list.html'
