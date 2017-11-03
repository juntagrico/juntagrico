# -*- coding: utf-8 -*-

from django.db.models import Sum, Case, When
from django.utils import timezone

from juntagrico.models import *
from juntagrico.util import temporal


class MemberDao:

    @staticmethod
    def all_members():
        return Member.objects.all()

    @staticmethod
    def members_by_email(email):
        return Member.objects.filter(email=email)

    @staticmethod
    def members_by_job(job):
        return Member.objects.filter(assignment__job=job)

    @staticmethod
    def members_for_subscription(subscription):
        return Member.objects.filter(Q(subscription=None) | Q(subscription=subscription))

    @staticmethod
    def members_for_email():
        return Member.objects.exclude(block_emails=True)

    @staticmethod
    def members_for_email_with_subscription():
        return Member.objects.exclude(subscription=None).filter(subscription__active=True).exclude(block_emails=True)

    @staticmethod
    def members_with_assignments_count():
        return MemberDao.annotate_members_with_assignemnt_count(Member.objects.all())

    @staticmethod
    def members_with_assignments_count_for_depot(depot):
        return MemberDao.annotate_members_with_assignemnt_count(Member.objects.filter(subscription__depot=depot))

    @staticmethod
    def members_with_assignments_count_in_area(area):
        return MemberDao.annotate_members_with_assignemnt_count(area.members.all())

    @staticmethod
    def members_with_assignments_count_in_subscription(subscription):
        return MemberDao.annotate_members_with_assignemnt_count(subscription.members.all())

    @staticmethod
    def annotate_members_with_assignemnt_count(members):
        now = timezone.now()
        return members.annotate(assignment_count=Sum(
            Case(When(assignment__job__time__gte=temporal.start_of_business_year(), assignment__job__time__lt=now, then='assignment__amount')))).annotate(
            core_assignment_count=Sum(Case(
                When(assignment__job__time__gte=temporal.start_of_business_year(), assignment__job__time__lt=now, assignment__core_cache=True,
                     then='assignment__amount'))))
