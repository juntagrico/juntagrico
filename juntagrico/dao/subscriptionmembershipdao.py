import datetime

from django.db.models import Q, F

from juntagrico.entity.member import SubscriptionMembership


class SubscriptionMembershipDao:

    @staticmethod
    def q_joined():
        return Q(join_date__isnull=False, join_date__lte=datetime.date.today())

    @staticmethod
    def q_left():
        return Q(leave_date__isnull=False, leave_date__lte=datetime.date.today())

    @classmethod
    def current_of_members(cls, members):
        return SubscriptionMembership.objects.filter(
            cls.q_joined() & ~cls.q_left(),
            member__in=members
        ).annotate(
            depot_name=F('subscription__depot__name')
        )
