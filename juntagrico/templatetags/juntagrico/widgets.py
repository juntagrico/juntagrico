import datetime

from django import template

from juntagrico.dao.jobdao import JobDao
from juntagrico.entity.member import Member
from juntagrico.entity.subs import Subscription

register = template.Library()


@register.simple_tag
def next_jobs(request):
    return JobDao.upcoming_jobs_for_member(request.user.member)


@register.filter
def remaining_assignments(sub):
    return max(
        sub.required_assignments - sub.assignment_count,
        sub.required_core_assignments - sub.core_assignment_count,
        0  # negative values would hide additionally made assignments
    )


@register.simple_tag
def assignment_progress(member, future=None, start=None, end=None, subscription=None):
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
    today = datetime.date.today()
    count_jobs_until = None if future is None else today
    count_jobs_from = today + datetime.timedelta(1)
    sub = subscription or member.subscription_current
    if sub:
        # annotate assignments of subscription with progress
        subs = Subscription.objects.annotate_assignments_progress(start, end, count_jobs_until=count_jobs_until)
        # annotate member assignment count and progress
        subs = subs.annotate_assignments_progress(start, end, member, count_jobs_until=count_jobs_until, prefix='member_')
        if future is True:
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
                        sub,
                        f + 'partner_' + core + attr,
                        getattr(sub, f + core + attr) - getattr(sub, f + 'member_' + core + attr)
                    )
    else:
        # get assignment count for member without sub
        m = Member.objects.annotate_assignment_count(start, count_jobs_until)
        if future is True:
            m = m.annotate_assignment_count(count_jobs_from, end, prefix='future_')
        member = m.get(pk=member.pk)
    return dict(
        subscription=sub,
        member=member,
        future=future
    )
