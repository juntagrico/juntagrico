from django.template.loader import get_template
from django.utils import timezone

from juntagrico.entity.member import Member


def home_messages(request):
    result = []
    member = request.user.member
    if member.confirmed is False:
        result.append(get_template('messages/not_confirmed.html').render())
    if member.subscription_current is None and member.subscription_future is None:
        result.append(get_template('messages/no_subscription.html').render())
    unpaid_shares = member.shares.unpaid().count()
    if unpaid_shares > 0:
        render_dict = {
            'amount': unpaid_shares,
        }
        template = get_template('messages/unpaid_shares.html')
        render_result = template.render(render_dict)
        result.append(render_result)
    return result


def job_messages(request, job):
    result = []
    member = request.user.member
    assignments = Member.objects.in_job(job).filter(pk=member.pk).count()
    if assignments:
        render_dict = {
            'amount': assignments - 1,
        }
        result = [get_template('messages/job_assigned.html').render(render_dict)]
    elif job.canceled:
        result = [get_template('messages/job_canceled.html').render()]
    elif job.end_time() < timezone.now():
        result = [get_template('messages/job_past.html').render()]
    elif job.start_time() < timezone.now():
        result = [get_template('messages/job_running.html').render()]
    elif job.free_slots == 0:
        result = [get_template('messages/job_fully_booked.html').render()]
    return result


def error_message(request):
    result = [get_template('messages/error.html').render()]
    return result
