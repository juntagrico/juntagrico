from django.db.models import Q, Min, Max
from django.utils import timezone
from polymorphic.query import PolymorphicQuerySet


class ShareQuerySet(PolymorphicQuerySet):
    def unpaid(self):
        return self.filter(paid_date__isnull=True)

    def paid(self):
        return self.filter(paid_date__isnull=False)

    def usable(self):
        """ not cancelled yet
        """
        return self.filter(cancelled_date__isnull=True)

    def active(self):
        """ paid and not paid back yet
        """
        return self.paid().filter(payback_date__isnull=True)

    def valid(self):
        """ ordered and not terminated yet
        """
        return self.filter(Q(termination_date__isnull=True) | Q(termination_date__gt=timezone.now()))

    def active_on(self, date=None):
        date = date or timezone.now()
        return self.filter(paid_date__lte=date).filter(Q(payback_date__isnull=True) | Q(payback_date__gte=date))

    def cancelled(self):
        """ cancelled but not paid back
        """
        return self.filter(cancelled_date__isnull=False, payback_date__isnull=True)

    def years(self, until=None):
        """
        :param until: maximum year for list
        :return: list of years spanning from the first to the last year one of the given shares was active
        """
        dates = self.paid().aggregate(Min('paid_date'), Max('payback_date'))
        if dates['paid_date__min']:
            until = until or timezone.now().year
            if dates['payback_date__max']:
                until = min(dates['payback_date__max'].year, until)
            return list(range(dates['paid_date__min'].year, until + 1))
        return []
