import math

from django import template
from django.utils import timezone

from juntagrico.dao.jobdao import JobDao

register = template.Library()


@register.simple_tag
def next_jobs(request):
    return JobDao.upcomming_jobs_for_member(request.user.member)


@register.simple_tag
def assignment_data(request):
    member = request.user.member
    current_sub = member.subscription_current
    if current_sub is None:
        return None

    # collect assignments
    recipients = current_sub.members_for_state.annotate_assignment_count(timezone.now())

    a = dict(partner_core=0, partner=0)
    for recipient in recipients:
        if recipient == member:
            a['member_core'] = recipient.core_assignment_count
            a['member'] = recipient.assignment_count
        else:
            a['partner_core'] += recipient.core_assignment_count
            a['partner'] += recipient.assignment_count

    # calculate remaining assignments
    remaining = current_sub.required_assignments - a['member'] - a['partner']
    remaining_core = current_sub.required_core_assignments - a['member_core'] - a['partner_core']

    # for displaying
    total = a['member'] + a['partner'] + max(remaining, remaining_core)
    a.update({
        'partner_core_bound': a['member'] + a['partner_core'],
        'partner_bound': a['member'] + a['partner'],
        'total': list(range(math.ceil(total))),
    })
    return a
