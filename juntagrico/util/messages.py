# -*- coding: utf-8 -*-

from django.template.loader import get_template
from django.utils import timezone

from juntagrico.dao.sharedao import ShareDao
from juntagrico.dao.memberdao import MemberDao


def home_messages(request):
    result = []
    member = request.user.member
    if member.confirmed is False:
        result.append(get_template('messages/not_confirmed.html').render())
    if member.subscription is None and member.future_subscription is None:
        result.append(get_template('messages/no_subscription.html').render())
    if len(ShareDao.unpaid_shares(member)) > 0:
        render_dict = {
            'amount': len(ShareDao.unpaid_shares(member)),
        }
        template = get_template('messages/unpaid_shares.html')
        render_result = template.render(render_dict)
        result.append(render_result)
    return result


def job_messages(request, job):
    result = []
    member = request.user.member
    all_participants = list(MemberDao.members_by_job(job))
    number_of_participants = len(all_participants)
    allowed_additional_participants = list(
        range(1, job.slots - number_of_participants + 1))
    if job.canceled:
        result.append(get_template('messages/job_canceled.html').render())
    elif job.end_time() < timezone.now():
        result.append(get_template('messages/job_past.html').render())
    elif job.start_time() < timezone.now():
        result.append(get_template('messages/job_running.html').render())
    if member in all_participants:
        render_dict = {
            'amount': all_participants.count(member)-1,
        }
        template = get_template('messages/job_assigned.html')
        render_result = template.render(render_dict)
        result.append(render_result)

    if len(allowed_additional_participants) == 0 and not job.canceled:
        result.append(get_template('messages/job_fully_booked.html').render())
    return result
