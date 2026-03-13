import datetime

from django.db.models import QuerySet


class MembershipQueryset(QuerySet):
    def active(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.filter(activation_date__lte=on_date).exclude(deactivation_date__lt=on_date)

    def requested(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.exclude(activation_date__lte=on_date)

    def active_or_requested(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.exclude(deactivation_date__lt=on_date)

    def canceled(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.filter(cancellation_date__isnull=False).exclude(deactivation_date__lt=on_date)

    def inactive(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.filter(deactivation_date__lte=on_date)
