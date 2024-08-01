import datetime

from django.db.models import ExpressionWrapper, Q, BooleanField
from polymorphic.query import PolymorphicQuerySet


class ShareQueryset(PolymorphicQuerySet):
    def active(self):
        return self.filter(paid_date__isnull=False, payback_date__isnull=True)

    def unpaid(self):
        return self.filter(paid_date__isnull=True)

    def usable(self):
        """ :return: shares that have been ordered (i.e. created) and not canceled yet
        """
        return self.filter(cancelled_date__isnull=True)

    def canceled(self):
        return self.filter(
            paid_date__isnull=False,
            cancelled_date__isnull=False,
            payback_date__isnull=True
        )

    def potentially_pending_payback(self):
        return self.filter(payback_date__isnull=True)

    def annotate_backpayable(self, on_date=None):
        """Share must be terminated before it can be paid back"""
        on_date = on_date or datetime.date.today()
        return self.annotate(backpayable=ExpressionWrapper(
            Q(termination_date__lte=on_date),
            output_field=BooleanField(),
        ))
