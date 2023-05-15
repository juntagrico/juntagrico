import datetime

from django import template
from django.utils import timezone

from juntagrico.dao.jobdao import JobDao
from juntagrico.entity.subs import Subscription

register = template.Library()


@register.simple_tag
def next_jobs(request):
    return JobDao.upcomming_jobs_for_member(request.user.member)


@register.simple_tag
def assignment_data(request):
    member = request.user.member
    if member.subscription_current is None:
        return None

    # calculate assignments
    sub = Subscription.objects.annotate_assignment_counts(
        of_member=member,
        end=timezone.now().date(),
        prefix='member_'
    ).annotate_assignments_progress().get(pk=member.subscription_current)
    sub.remaining_assignments = max(
        sub.required_assignments - sub.assignment_count,
        sub.required_core_assignments - sub.core_assignment_count,
        0  # negative values would hide additionally made assignments
    )

    # for displaying
    return {
        'member_core': int(sub.member_core_assignment_count),
        'member': int(sub.member_assignment_count),
        'partner_core': int(sub.core_assignment_count - sub.member_core_assignment_count),
        'partner': int(sub.assignment_count - sub.member_assignment_count),
        'partner_core_bound': int(sub.member_assignment_count + sub.core_assignment_count - sub.member_core_assignment_count),
        'partner_bound': int(sub.assignment_count),
        'total': list(range(int(sub.assignment_count + sub.remaining_assignments))),
    }


@register.inclusion_tag('widgets/assignments.html')
def assignments(member, future=None, start=None, end=None, subscription=None):
    """
    Display the satus of completed assignment for a given member.
    :param member: member instance of which the assignment status should be displayed
    :param future: None: display all assignments in period,
                   False: display only past assignments,
                   True: display future assignments separately.
    :param start: beginning of period of interest, default: start of current business year.
    :param end: end of period of interest, default: end of current business year.
    :param subscription: subscription of which the assignment status should be calculated. Default=member.subscription_current.
    :return:
    """
    sub = subscription or member.subscription_current
    if sub:
        today = timezone.now().date()
        count_jobs_until = None if future is None else today
        # annotate assignments of subscription with progress
        subs = Subscription.objects.annotate_assignments_progress(start, end, count_jobs_until=count_jobs_until)
        # annotate member assignment count and progress
        subs = subs.annotate_assignments_progress(start, end, member, count_jobs_until, prefix='member_')
        if future is True:
            count_jobs_from = today + datetime.timedelta(1)
            # annotate future assignment count and progress of subscription separately
            subs = subs.annotate_assignments_progress(start, end, count_jobs_from=count_jobs_from, prefix='future_')
            # annotate future member assignment count and progress
            subs = subs.annotate_assignments_progress(start, end, member, count_jobs_from=count_jobs_from, prefix='future_member_')
        # get result
        sub = subs.get(pk=sub)

    # calculate values for display: partner = total - member
    for core in ['', 'core_']:
        for f in ['', 'future_'] if future is True else ['']:
            for attr in ['assignment_count', 'assignments_progress']:
                setattr(
                    sub, f + 'partner_' + core + attr,
                    getattr(sub, f + core + attr) - getattr(sub, f + 'member_' + core + attr)
                )
    return dict(
        sub=sub,
        future=future
    )
