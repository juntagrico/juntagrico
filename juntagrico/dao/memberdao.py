import datetime

from django.contrib.auth.models import Permission
from django.db.models import Q

from juntagrico.entity.member import Member
from juntagrico.queryset.member import q_subscription_activated, q_subscription_deactivated


class MemberDao:
    @staticmethod
    def q_subscription_canceled():
        return Q(subscriptionmembership__subscription__cancellation_date__isnull=False,
                 subscriptionmembership__subscription__cancellation_date__lte=datetime.date.today())

    @staticmethod
    def has_future_subscription():
        return Q(~q_subscription_activated(),
                 ~MemberDao.q_subscription_canceled(),
                 ~q_subscription_deactivated(),
                 subscriptionmembership__isnull=False)

    @staticmethod
    def member_by_email(email):
        return next(iter(Member.objects.filter(email__iexact=email) or []), None)

    @staticmethod
    def members_in_subscription(subscription):
        return Member.objects.filter(subscriptionmembership__subscription=subscription)

    @staticmethod
    def members_by_permission(permission_codename):
        perm = Permission.objects.get(codename=permission_codename)
        return Member.objects.filter(Q(user__groups__permissions=perm) | Q(user__user_permissions=perm)).distinct()
