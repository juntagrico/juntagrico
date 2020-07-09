from datetime import datetime, time

from django.contrib.auth.models import Permission
from django.db.models import Sum, Case, When, Q
from django.utils import timezone
from django.utils.timezone import get_default_timezone as gdtz

from juntagrico.entity.member import Member
from juntagrico.util.temporal import start_of_business_year


class MemberDao:

    @staticmethod
    def all_members():
        return Member.objects.all()

    @staticmethod
    def canceled_members():
        return Member.objects.filter(canceled=True).exclude(inactive=True)

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
    def members_for_subscription(subscription):
        return Member.objects.filter((Q(subscription=None) & Q(future_subscription=None)) | Q(subscription=subscription))

    @staticmethod
    def members_for_future_subscription(subscription):
        return Member.objects.filter((Q(subscription=None) | Q(subscription__cancellation_date__isnull=False))
                                     & Q(future_subscription=None) | Q(future_subscription=subscription))

    @staticmethod
    def members_for_create_subscription():
        return Member.objects.filter((Q(subscription=None) | Q(subscription__cancellation_date__isnull=False))
                                     & Q(future_subscription=None))

    @staticmethod
    def members_for_email():
        return Member.objects.exclude(inactive=True)

    @staticmethod
    def members_for_email_with_subscription():
        return Member.objects.exclude(subscription=None).filter(subscription__activation_date__isnull=False).exclude(inactive=True)

    @staticmethod
    def members_for_email_with_shares():
        return Member.objects.filter(share__isnull=False).exclude(inactive=True)

    @staticmethod
    def members_with_assignments_count():
        return MemberDao.annotate_members_with_assignemnt_count(Member.objects.all())

    @staticmethod
    def active_members_with_assignments_count():
        return MemberDao.annotate_members_with_assignemnt_count(Member.objects.filter(inactive=False))

    @staticmethod
    def members_with_assignments_count_for_depot(depot):
        return MemberDao.annotate_members_with_assignemnt_count(Member.objects.filter(subscription__depot=depot).filter(inactive=False))

    @staticmethod
    def members_with_assignments_count_in_area(area):
        return MemberDao.annotate_members_with_assignemnt_count(area.members.all().filter(inactive=False))

    @staticmethod
    def members_with_assignments_count_in_subscription(subscription):
        return MemberDao.annotate_members_with_assignemnt_count(subscription.members.all())

    @staticmethod
    def annotate_members_with_assignemnt_count(members):
        now = timezone.now()
        start = gdtz().localize(datetime.combine(start_of_business_year(), time.min))
        return members.annotate(assignment_count=Sum(
            Case(When(assignment__job__time__gte=start, assignment__job__time__lt=now, then='assignment__amount')))).annotate(
            core_assignment_count=Sum(Case(
                When(assignment__job__time__gte=start, assignment__job__time__lt=now, assignment__core_cache=True,
                     then='assignment__amount'))))

    @staticmethod
    def members_by_permission(permission_codename):
        perm = Permission.objects.get(codename=permission_codename)
        return Member.objects.filter(Q(user__groups__permissions=perm) | Q(user__user_permissions=perm)).distinct()
