
from django.db.models import Q
from django.utils import timezone
from juntagrico.entity.member import SubscriptionMembership


class SubscriptionMembershipDao:

    @staticmethod
    def get_other_waiting_for_member(member, subscription):
        join_date_isnull = Q(join_date__isnull=True)
        join_date_future = Q(join_date__gt=timezone.now().date())
        return SubscriptionMembership.objects.exclude(subscription=subscription) \
            .filter(join_date_isnull | join_date_future) \
            .filter(member=member)

    @staticmethod
    def get_other_active_for_member(member, subscription):
        join_date_notnull = Q(join_date__isnull=False)
        join_date_present = Q(join_date__lte=timezone.now().date())
        leave_date_isnull = Q(leave_date__isnull=True)
        leave_date_future = Q(leave_date__gt=timezone.now().date())
        return SubscriptionMembership.objects.exclude(subscription=subscription) \
            .filter(join_date_notnull & join_date_present) \
            .filter(leave_date_isnull | leave_date_future) \
            .filter(member=member)

    @staticmethod
    def get_all_for_subscription(subscription):
        return SubscriptionMembership.objects.filter(subscription=subscription)
