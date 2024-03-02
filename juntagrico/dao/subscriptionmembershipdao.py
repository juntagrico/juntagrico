import datetime

from django.db.models import Q, F

from juntagrico.entity.member import SubscriptionMembership, q_joined_subscription, q_left_subscription


class SubscriptionMembershipDao:

    @staticmethod
    def q_joined():
        return Q(join_date__isnull=False, join_date__lte=datetime.date.today())

    @staticmethod
    def q_left():
        return Q(leave_date__isnull=False, leave_date__lte=datetime.date.today())

    @staticmethod
    def get_other_waiting_for_member(member, subscription):
        return SubscriptionMembership.objects.exclude(subscription=subscription) \
            .filter(~q_joined_subscription()) \
            .filter(member=member)

    @staticmethod
    def get_other_active_for_member(member, subscription, asof=None):
        return SubscriptionMembership.objects.exclude(subscription=subscription) \
            .filter(q_joined_subscription() & ~q_left_subscription(asof)) \
            .filter(member=member)

    @staticmethod
    def get_all_for_subscription(subscription):
        return SubscriptionMembership.objects.filter(subscription=subscription)

    @classmethod
    def current_of_members(cls, members):
        return SubscriptionMembership.objects.filter(
            cls.q_joined() & ~cls.q_left(),
            member__in=members
        ).annotate(
            depot_name=F('subscription__depot__name')
        )
