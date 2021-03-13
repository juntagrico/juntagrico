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
    required_assignments = 0
    userassignments = AssignmentDao.assignments_for_member_current_business_year(
        member)
    if member.subscription_current is not None:
        partner_assignments = []
        for subscription_member in member.subscription_current.recipients_all:
            if subscription_member == member:
                continue
            partner_assignments.extend(
                AssignmentDao.assignments_for_member_current_business_year(subscription_member))
        required_assignments = member.subscription_current.required_assignments
    else:
        partner_assignments = []

    userassignments_total = int(sum(a.amount for a in userassignments))
    userassignemnts_core = int(
        sum(a.amount for a in userassignments if a.is_core()))
    partner_assignments_total = int(sum(a.amount for a in partner_assignments))
    partner_assignments_core = int(
        sum(a.amount for a in partner_assignments if a.is_core()))
    assignmentsrange = list(range(
        0, max(required_assignments, userassignments_total + partner_assignments_total)))
    return {
        'assignmentsrange': assignmentsrange,
        'userassignments_bound': userassignments_total,
        'userassignemnts_core_bound': userassignemnts_core,
        'partner_assignments_bound': userassignments_total + partner_assignments_total,
        'partner_assignments_core_bound': userassignments_total + partner_assignments_core
    }
