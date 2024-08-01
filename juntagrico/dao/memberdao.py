import datetime

from django.contrib.auth.models import Permission
from django.db.models import Q

from juntagrico.entity.member import Member
from juntagrico.util.models import q_deactivated


class MemberDao:

    @staticmethod
    def q_joined_subscription():
        return Q(subscriptionmembership__join_date__isnull=False,
                 subscriptionmembership__join_date__lte=datetime.date.today())

    @staticmethod
    def q_left_subscription():
        return Q(subscriptionmembership__leave_date__isnull=False,
                 subscriptionmembership__leave_date__lte=datetime.date.today())

    @staticmethod
    def q_subscription_activated():
        return Q(subscriptionmembership__subscription__activation_date__isnull=False,
                 subscriptionmembership__subscription__activation_date__lte=datetime.date.today())

    @staticmethod
    def q_subscription_canceled():
        return Q(subscriptionmembership__subscription__cancellation_date__isnull=False,
                 subscriptionmembership__subscription__cancellation_date__lte=datetime.date.today())

    @staticmethod
    def q_subscription_deactivated():
        return Q(subscriptionmembership__subscription__deactivation_date__isnull=False,
                 subscriptionmembership__subscription__deactivation_date__lte=datetime.date.today())

    @staticmethod
    def has_subscription():
        return Q(MemberDao.q_subscription_activated(),
                 ~MemberDao.q_subscription_canceled(),
                 ~MemberDao.q_subscription_deactivated(),
                 MemberDao.q_joined_subscription(),
                 ~MemberDao.q_left_subscription())

    @staticmethod
    def has_canceled_subscription():
        return Q(MemberDao.q_subscription_activated(),
                 MemberDao.q_subscription_canceled(),
                 ~MemberDao.q_subscription_deactivated(),
                 MemberDao.q_joined_subscription(),
                 ~MemberDao.q_left_subscription())

    @staticmethod
    def has_future_subscription():
        return Q(~MemberDao.q_subscription_activated(),
                 ~MemberDao.q_subscription_canceled(),
                 ~MemberDao.q_subscription_deactivated(),
                 subscriptionmembership__isnull=False)

    @staticmethod
    def all_members():
        return Member.objects.all()

    @staticmethod
    def member_by_email(email):
        return next(iter(Member.objects.filter(email__iexact=email) or []), None)

    @staticmethod
    def members_with_shares():
        return Member.objects.filter(Q(share__isnull=False) & (
            Q(share__termination_date__isnull=True) | Q(share__termination_date__gt=datetime.date.today())))

    @staticmethod
    def members_by_job(job):
        return Member.objects.filter(assignment__job=job)

    @staticmethod
    def members_in_subscription(subscription):
        return Member.objects.filter(subscriptionmembership__subscription=subscription)

    @staticmethod
    def members_for_email():
        return Member.objects.exclude(q_deactivated())

    @staticmethod
    def members_for_email_with_subscription():
        return Member.objects.filter(MemberDao.has_subscription() | MemberDao.has_canceled_subscription()).exclude(
            q_deactivated())

    @staticmethod
    def members_for_email_with_shares():
        return MemberDao.members_with_shares().exclude(q_deactivated())

    @staticmethod
    def member_with_active_subscription_for_depot(depot):
        return Member.objects.filter(MemberDao.has_subscription() | MemberDao.has_canceled_subscription(),
                                     subscriptionmembership__subscription__depot=depot)\
            .exclude(q_deactivated())

    @staticmethod
    def active_members():
        return Member.objects.filter(~q_deactivated())

    @staticmethod
    def members_in_area(area):
        return area.members.all().filter(~q_deactivated())

    @staticmethod
    def members_by_permission(permission_codename):
        perm = Permission.objects.get(codename=permission_codename)
        return Member.objects.filter(Q(user__groups__permissions=perm) | Q(user__user_permissions=perm)).distinct()
