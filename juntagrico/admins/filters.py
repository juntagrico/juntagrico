import datetime

from django.contrib.admin.filters import DateFieldListFilter
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
