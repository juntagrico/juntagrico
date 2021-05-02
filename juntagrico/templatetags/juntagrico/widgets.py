from django import template

from juntagrico.dao.assignmentdao import AssignmentDao
from juntagrico.dao.jobdao import JobDao

register = template.Library()


@register.simple_tag
def next_jobs(request):
    return JobDao.upcomming_jobs_for_member(request.user.member)


@register.simple_tag
def assignment_data(request):
    member = request.user.member
    if member.subscription_current is None:
        return None

    # collect assignments
    member_assignments = AssignmentDao.assignments_for_member_current_business_year(member)
    partner_assignments = []
    for subscription_member in member.subscription_current.co_members(member):
        partner_assignments.extend(
            AssignmentDao.assignments_for_member_current_business_year(subscription_member)
        )

    # count assignments
    assignments = {
        'member_core': int(sum(a.amount for a in member_assignments if a.is_core())),
        'member': int(sum(a.amount for a in member_assignments)),
        'partner_core': int(sum(a.amount for a in partner_assignments if a.is_core())),
        'partner': int(sum(a.amount for a in partner_assignments)),
    }

    # calculate remaining assignments
    remaining = member.subscription_current.required_assignments -\
        assignments['member'] - assignments['partner']
    remaining_core = member.subscription_current.required_core_assignments -\
        assignments['member_core'] - assignments['partner_core']

    # for displaying
    total = assignments['member'] + assignments['partner'] + max(remaining, remaining_core)
    assignments.update({
        'partner_core_bound': assignments['member'] + assignments['partner_core'],
        'partner_bound': assignments['member'] + assignments['partner'],
        'total': list(range(total)),
    })
    return assignments
