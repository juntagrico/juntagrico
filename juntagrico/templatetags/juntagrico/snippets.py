import datetime

from django import template
from impersonate.helpers import check_allow_for_user

from juntagrico.config import Config
from juntagrico.entity.jobs import Job, RecuringJob

register = template.Library()


@register.inclusion_tag('snippets/impersonation_link.html')
def impersonate_start(request, member):
    user = member.user
    return {
        'can_impersonate': check_allow_for_user(request, user),
        'user': user
    }


@register.inclusion_tag('juntagrico/job/snippets/participant_list.html')
def job_participant_list(user, job):
    participants = job.participants.annotate_job_slots()
    show_first_job = Config.first_job_info()
    if 'overall' in show_first_job:
        participants = participants.annotate_first_job()
    if 'per_area' in show_first_job:
        participants = participants.annotate_first_job('_in_area', Job.objects.in_area(job.type.activityarea))
    if 'per_type' in show_first_job and isinstance(job, RecuringJob):
        participants = participants.annotate_first_job('_of_type', job.type.recuringjob_set.all())
    permissions = job.check_if(user)
    return {
        'job': job,
        'participants': participants,
        'can_contact': permissions.can_contact_member(),
        'can_edit_assignments': permissions.can_modify_assignments(),
    }


@register.inclusion_tag('juntagrico/snippets/depot/fee.html')
def depot_fee(depot, subscription_count, prefix='', postfix=''):
    return {
        'fee': depot.total_fee(subscription_count),
        'prefix': prefix,
        'postfix': postfix
    }


@register.simple_tag
def subscription_depot_fee(subscription_type, depot=''):
    fee = 0
    if depot != '':
        condition = subscription_type.depot_conditions.filter(depot=depot).first()
        fee = condition.fee if condition else 0
    return fee


@register.inclusion_tag('juntagrico/snippets/action_date.html')
def action_date(request):
    change_date_string = request.session.get('changedate', None)
    date_changed = change_date_string is not None
    if date_changed:
        change_date = datetime.date.fromisoformat(change_date_string)
    else:
        change_date = datetime.date.today()
    return {'change_date': change_date, 'date_changed': date_changed}


@register.inclusion_tag('juntagrico/alert.html')
def alert(message):
    if message.level_tag == 'error':
        alert_lvl = 'danger'
    elif message.level_tag == 'debug':
        alert_lvl = 'secondary'
    else:
        alert_lvl = message.level_tag
    return {'message': message, 'alert_level': 'alert-' + alert_lvl}
