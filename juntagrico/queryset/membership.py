import datetime

from django.db.models import QuerySet, Subquery, OuterRef, Count
from django.db.models.functions import Coalesce

from juntagrico.config import Config


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

    def not_canceled(self):
        return self.filter(cancellation_date__isnull=True)

    def canceled(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.filter(cancellation_date__isnull=False).exclude(deactivation_date__lt=on_date)

    def inactive(self, on_date=None):
        on_date = on_date or datetime.date.today()
        return self.filter(deactivation_date__lte=on_date)

    def required_shares_count(self):
        if Config.membership('enable'):
            return self.count() * Config.membership('required_shares')
        return 0

    def annotate_shares(self):
        from juntagrico.entity.share import Share
        return self.annotate(
            ordered_shares=Coalesce(
                Subquery(
                    Share.objects.unpaid()
                    .usable()
                    .filter(member__memberships=OuterRef('pk'))
                    .values('member')
                    .annotate(count=Count('id'))
                    .values('count')
                ),
                0,
            ),
            paid_shares=Coalesce(
                Subquery(
                    Share.objects.active()
                    .filter(member__memberships=OuterRef('pk'))
                    .values('member')
                    .annotate(count=Count('id'))
                    .values('count')
                ),
                0,
            ),
            canceled_shares=Coalesce(
                Subquery(
                    Share.objects.active()
                    .canceled()
                    .filter(member__memberships=OuterRef('pk'))
                    .values('member')
                    .annotate(count=Count('id'))
                    .values('count')
                ),
                0,
            ),
        )