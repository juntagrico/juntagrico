from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.db.models import TextField
from djrichtextfield.widgets import RichTextWidget
from import_export.admin import ExportMixin

from juntagrico.admins.forms.import_export_form import ExportAssignmentDateRangeForm
from juntagrico.config import Config
from juntagrico.util import addons


class BaseAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        self.inlines = self.inlines or []
        self.inlines.extend(addons.config.get_model_inlines(model))
        super().__init__(model, admin_site)


class RichTextAdmin(BaseAdmin):

    def __init__(self, model, admin_site):
        if Config.using_richtext():
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

    def get_export_resource_kwargs(self, request, *args, **kwargs):
        form = kwargs.get('export_form')
        if form:
            kwargs.update(
                start_date=form.cleaned_data['export_start_date'],
                end_date=form.cleaned_data['export_end_date'],
            )
        return kwargs

    @staticmethod
    def get_export_date(post, name):
        return '-'.join([post.get(f"export_{name}_date_{i}") for i in ['year', 'month', 'day']])

    def get_export_filename(self, request, queryset, file_format):
        # add date range to filename
        ext = file_format.get_extension()
        start_date = self.get_export_date(request.POST, 'start')
        end_date = self.get_export_date(request.POST, 'end')
        return f'{super().get_export_filename(request, queryset, file_format)[:-len(ext) - 1]}--{start_date}--{end_date}.{ext}'


class SortableExportMixin(ExportMixin):
    """ Fix to make import-export and sortable admin work together.
    """
    change_list_template = 'adminsortable2/change_list.html'


class AreaCoordinatorMixin(BaseModelAdmin):
    # TODO: also show job contacts and job extras?
    coordinator_permissions = ['view', 'add', 'change', 'delete']
    path_to_area = 'pk'

    def _has_permission(self, request, obj=None, access=None):
        if access is None or access in self.coordinator_permissions:
            area = {'area': self.get_area(obj)} if obj else {}
            return request.user.member.area_access.filter(**area, can_modify_jobs=True).exists()
        return False

    def get_area(self, obj):
        return obj

    def has_module_permission(self, request):
        return self._has_permission(request) or super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return self._has_permission(request, obj, 'view') or super().has_view_permission(request)

    def has_add_permission(self, request):
        return self._has_permission(request, None, 'add') or super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return self._has_permission(request, obj, 'change') or super().has_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self._has_permission(request, obj, 'delete') or super().has_delete_permission(request)

    def get_queryset(self, request):
        if super().has_view_permission(request):
            return super().get_queryset(request)
        else:
            allowed_areas = request.user.member.coordinated_areas.filter(coordinator_access__can_modify_jobs=True)
            return super().get_queryset(request).filter(**{f'{self.path_to_area}__in': allowed_areas})


def can_see_all(user, model):
    return user.has_perm(f'juntagrico.view_{model}') or user.has_perm(f'juntagrico.change_{model}')
