import datetime

from django import template
from django.db.models import Q
from django.utils import timezone
from impersonate.helpers import check_allow_for_user

from juntagrico.config import Config
from juntagrico.entity.jobs import Job, RecuringJob, JobMessage
from juntagrico.forms.job import AddAssignmentForm, AddJobMessageForm

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
        'add_form': AddAssignmentForm(job) if permissions.can_add_assignments() else None,
        'other_job_contacts': job.get_emails(get_member=True, exclude=[user.member.email]),
        'can_view_members': user.has_perm('juntagrico.view_member') or user.has_perm('juntagrico.change_member')
    }


@register.inclusion_tag('juntagrico/job/snippets/messages.html')
def job_messages(user, job):
    permissions = job.check_if(user)
    member = user.member
    can_manage_messages = permissions.can_manage_messages()
    if can_manage_messages:
        messages = job.messages.all()
    else:
        messages = job.messages.filter(Q(is_public=True) | Q(account=member))

    show_messages = messages.exists()
    if show_messages and job.time + datetime.timedelta(hours=JobMessage.KEEP_HOURS) < timezone.now():
        # delete old messages just in time
        JobMessage.purge()
        show_messages = messages.exists()

    message_form = None
    if member in job.participants and not job.has_ended():
        message_form = AddJobMessageForm()
        show_messages = True

    return {
        'job': job,
        'member': member,
        'show_messages': show_messages,
        'message_form': message_form,
        'can_manage_messages': can_manage_messages,
        'can_contact': permissions.can_contact_member(),
        'messages': messages.order_by('created_at'),
        'other_job_contacts': job.get_emails(get_member=True, exclude=[member.email]),
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


@register.inclusion_tag('juntagrico/snippets/external_link.html')
def ext_link(text, link):
    return {'text': text, 'link': link}


@register.inclusion_tag('juntagrico/manage/share/snippets/summary.html')
def share_summary(account):
    ordered_shares = account.shares.unpaid().usable()
    active_shares = account.shares.active()
    canceled_shares = account.shares.canceled()
    return {
        'ordered_shares': ordered_shares,
        'active_shares': active_shares,
        'canceled_shares': canceled_shares,
    }


@register.simple_tag
def sequence(array, attribute=None, prefix='', postfix='', sep=', ', range_sep='-'):
    if attribute is not None:
        array = [getattr(item, attribute) for item in array]
    array = sorted(array)

    array_len = len(array)
    result = []
    i = 0
    while i < array_len:
        j = i
        while j + 1 < array_len and array[j] + 1 == array[j + 1]:
            j += 1
        if j - i > 1:
            result.append(f'{prefix}{array[i]}{postfix}{range_sep}{prefix}{array[j]}{postfix}')
        else:
            result += [f'{prefix}{item}{postfix}' for item in array[i:j + 1]]
        i = j + 1

    return sep.join(result)
