import datetime

from django.db.models import ExpressionWrapper, Q, BooleanField
from polymorphic.query import PolymorphicQuerySet

from juntagrico.config import Config


class ShareQueryset(PolymorphicQuerySet):
    def active(self):
        return self.filter(paid_date__isnull=False, payback_date__isnull=True)

    def paid(self):
        return self.filter(paid_date__isnull=False)

    def unpaid(self):
        return self.filter(paid_date__isnull=True)

    def usable(self):
        """ :return: shares that have been ordered (i.e. created) and not canceled yet
        """
        return self.filter(cancelled_date__isnull=True)

    def canceled(self):
        return self.active().filter(cancelled_date__isnull=False)

    def potentially_pending_payback(self):
        return self.filter(payback_date__isnull=True)

    def annotate_backpayable(self, on_date=None):
        """Share must be terminated before it can be paid back"""
        on_date = on_date or datetime.date.today()
        return self.annotate(backpayable=ExpressionWrapper(
            Q(termination_date__lte=on_date, paid_date__isnull=False, payback_date__isnull=True),
            output_field=BooleanField(),
        ))

    def count_dedicated(self, to_subscription=None, only_total=False):
        if to_subscription is not None:
            current_members = to_subscription.current_members
        else:
            current_members = getattr(self, '_bound_members', [])

        undedicated = 0
        if Config.cumulative_shares_for_membership():
            from juntagrico.entity.membership import Membership
            # if cumulative, subtract shares that are needed for membership
            undedicated = Membership.objects.filter(
                account__in=current_members
            ).not_canceled().count() * Config.membership('required_shares')

        total = self.usable().count() - undedicated
        if only_total:
            return total
        return {
            'paid': self.usable().paid().count() - undedicated,
            'total': total
        }
