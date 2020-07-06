import datetime

from django.contrib.admin.filters import DateFieldListFilter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class FutureDateTimeFilter(DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = timezone.now().date()

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
