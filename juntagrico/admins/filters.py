import datetime

from django.contrib.admin.filters import DateFieldListFilter, SimpleListFilter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class FutureDateTimeFilter(DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        # https://github.com/django/django/blob/main/django/contrib/admin/filters.py#L471
        if timezone.is_aware(now):
            now = timezone.localtime(now)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        self.links = self.links[:1] + (
            (_('Nächste 30 Tage'), {
                self.lookup_kwarg_since: str(today),
                self.lookup_kwarg_until: str(today + datetime.timedelta(days=30)),
            }),
            (_('Nächste 7 Tage'), {
                self.lookup_kwarg_since: str(today),
                self.lookup_kwarg_until: str(today + datetime.timedelta(days=7)),
            }),
        ) + self.links[1:]


class SimpleStateModelFilter(SimpleListFilter):
    title = _("Status")
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return [
            ("waiting", _("Wartend")),
            ("future", _("Wartend oder aktiv")),
            ("active", _("Aktiv")),
            ("inactive", _("Inaktiv")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "waiting":
            return queryset.filter(activation_date=None)
        if self.value() == "future":
            return queryset.filter(deactivation_date=None)
        if self.value() == "active":
            return queryset.active()
        if self.value() == "inactive":
            return queryset.exclude(deactivation_date=None)
