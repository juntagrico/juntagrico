from datetime import datetime, time

from django.contrib.auth.models import Permission
from django.db.models import Sum, Case, When, Q
from django.utils import timezone
from django.utils.timezone import get_default_timezone as gdtz

from juntagrico.entity.member import Member
from juntagrico.util.models import PropertyQuerySet, q_deactivated
from juntagrico.util.models import q_cancelled
from juntagrico.util.temporal import start_of_business_year, end_of_business_year


class MemberDao:

    @staticmethod
    def q_joined_subscription():
        return Q(subscriptionmembership__join_date__isnull=False,
                 subscriptionmembership__join_date__lte=timezone.now().date())

    @staticmethod
    def q_left_subscription():
        return Q(subscriptionmembership__leave_date__isnull=False,
                 subscriptionmembership__leave_date__lte=timezone.now().date())

    @staticmethod
    def q_subscription_activated():
        return Q(subscriptionmembership__subscription__activation_date__isnull=False,
                 subscriptionmembership__subscription__activation_date__lte=timezone.now().date())

    @staticmethod
    def q_subscription_cancelled():
        return Q(subscriptionmembership__subscription__cancellation_date__isnull=False,
                 subscriptionmembership__subscription__cancellation_date__lte=timezone.now().date())

    @staticmethod
    def q_subscription_deactivated():
        return Q(subscriptionmembership__subscription__deactivation_date__isnull=False,
                 subscriptionmembership__subscription__deactivation_date__lte=timezone.now().date())

    @staticmethod
    def has_subscription():
        return Q(MemberDao.q_subscription_activated(),
                 ~MemberDao.q_subscription_cancelled(),
                 ~MemberDao.q_subscription_deactivated(),
                 MemberDao.q_joined_subscription(),
                 ~MemberDao.q_left_subscription())

    @staticmethod
    def has_cancelled_subscription():
        return Q(MemberDao.q_subscription_activated(),
                 MemberDao.q_subscription_cancelled(),
                 ~MemberDao.q_subscription_deactivated(),
                 MemberDao.q_joined_subscription(),
                 ~MemberDao.q_left_subscription())

    @staticmethod
    def has_future_subscription():
        return Q(~MemberDao.q_subscription_activated(),
                 ~MemberDao.q_subscription_cancelled(),
                 ~MemberDao.q_subscription_deactivated(),
                 subscriptionmembership__isnull=False)

    @staticmethod
    def all_members():
        result = PropertyQuerySet.from_qs(Member.objects.all())
        result.set_property('name', 'all')
        result.set_property('subscription_id', '')
        return result

    @staticmethod
    def canceled_members():
        return Member.objects.filter(q_cancelled()).exclude(q_deactivated())

    @staticmethod
    def member_by_email(email):
        return next(iter(Member.objects.filter(email__iexact=email) or []), None)

    @staticmethod
    def members_with_shares():
        return Member.objects.filter(share__isnull=False)

    @staticmethod
    def members_by_job(job):
        return Member.objects.filter(assignment__job=job)

    @staticmethod
    def members_in_subscription(subscription):
        return Member.objects.filter(subscriptionmembership__subscription=subscription)

    @staticmethod
    def members_for_subscription(subscription):
        result = PropertyQuerySet.from_qs(Member.objects.filter(
            (~MemberDao.has_subscription() & ~MemberDao.has_cancelled_subscription() & ~MemberDao.has_future_subscription()) | Q(
                subscriptionmembership__subscription=subscription)).distinct())
        result.set_property('name', 's')
        result.set_property('subscription_id', str(subscription.pk))
        return result

    @staticmethod
    def members_for_future_subscription(subscription):
        result = PropertyQuerySet.from_qs(Member.objects.filter(
            (~MemberDao.has_subscription() | MemberDao.has_cancelled_subscription()) & ~MemberDao.has_future_subscription() | Q(
                subscriptionmembership__subscription=subscription)).distinct())
        result.set_property('name', 'fs')
        result.set_property('subscription_id', str(subscription.pk))
        return result

    @staticmethod
    def members_for_create_subscription():
        result = PropertyQuerySet.from_qs(Member.objects.filter(
            (~MemberDao.has_subscription() | MemberDao.has_cancelled_subscription()) & ~MemberDao.has_future_subscription()).distinct())
        result.set_property('name', 'cs')
        result.set_property('subscription_id', '')
        return result

    @staticmethod
    def members_for_email():
        return Member.objects.exclude(q_deactivated())

    @staticmethod
    def members_for_email_with_subscription():
        return Member.objects.filter(MemberDao.has_subscription() | MemberDao.has_cancelled_subscription()).exclude(
            q_deactivated())

    @staticmethod
    def members_for_email_with_shares():
        return Member.objects.filter(share__isnull=False).exclude(q_deactivated())

    @staticmethod
    def member_with_active_subscription_for_depot(depot):
        return Member.objects.filter(MemberDao.has_subscription() | MemberDao.has_cancelled_subscription(),
                                     subscriptionmembership__subscription__depot=depot)\
            .exclude(q_deactivated())

    @staticmethod
    def members_with_assignments_count():
        return MemberDao.annotate_members_with_assignemnt_count(Member.objects.all())

    @staticmethod
    def active_members():
        return Member.objects.filter(~q_deactivated())

    @staticmethod
    def members_in_area(area):
        return area.members.all().filter(~q_deactivated())

    @staticmethod
    def members_with_assignments_count_in_subscription(subscription):
        return MemberDao.annotate_members_with_assignemnt_count(MemberDao.members_in_subscription(subscription))

    @staticmethod
    def annotate_members_with_assignemnt_count(members):
        start = gdtz().localize(datetime.combine(start_of_business_year(), time.min))
        end = gdtz().localize(datetime.combine(end_of_business_year(), time.max))
        return members.annotate(assignment_count=Sum(
            Case(When(assignment__job__time__gte=start,
                      assignment__job__time__lt=end,
                      then='assignment__amount')))).annotate(
            core_assignment_count=Sum(Case(
                When(assignment__job__time__gte=start,
                     assignment__job__time__lt=end,
                     assignment__core_cache=True,
                     then='assignment__amount'))))

    @staticmethod
    def members_by_permission(permission_codename):
        perm = Permission.objects.get(codename=permission_codename)
        return Member.objects.filter(Q(user__groups__permissions=perm) | Q(user__user_permissions=perm)).distinct()
