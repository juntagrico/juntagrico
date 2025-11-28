from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.template import Template, Context
from django.utils.translation import ngettext, gettext as _
from django_select2.views import AutoResponseView

from juntagrico.entity.depot import Depot
from juntagrico.entity.jobs import Job
from juntagrico.entity.mailing import MailTemplate
from juntagrico.entity.member import Member
from juntagrico.forms.email import EmailForm, RecipientsForm, DepotForm, BaseForm, DepotRecipientsForm, AreaForm, \
    AreaRecipientsForm, JobForm, JobRecipientsForm, MemberForm
from juntagrico.view_decorators import requires_permission_to_contact


class InternalSelect2View(LoginRequiredMixin, AutoResponseView):
    """Limit access to autocomplete (select2) to logged-in users
    """
    pass


@requires_permission_to_contact
def count_recipients(request, form=None):
    form = form or RecipientsForm(request.user.member, data=request.GET)
    if form.is_valid():
        if count := form.count_recipients():
            return HttpResponse(ngettext(
                'An {} Person senden',
                'An {} Personen senden',
                count
            ).format(count))
    return HttpResponse(_('Senden'))


@requires_permission_to_contact
def count_depot_recipients(request, depot_id):
    form = DepotRecipientsForm(request.user.member, depot_id, data=request.GET)
    return count_recipients(request, form)


@requires_permission_to_contact
def count_area_recipients(request, area_id):
    form = AreaRecipientsForm(request.user.member, area_id, data=request.GET)
    return count_recipients(request, form)


@requires_permission_to_contact
def count_job_recipients(request, job_id):
    form = JobRecipientsForm(request.user.member, job_id, data=request.GET)
    return count_recipients(request, form)


@login_required
def to_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if not request.user.member.can_contact(member):
        raise PermissionDenied
    return email_view(request, MemberForm, {
        'to_members': [member_id]
    })


@login_required
def to_depot(request, depot_id):
    if not request.user.member.can_contact(depot_id=depot_id):
        raise PermissionDenied
    members = request.GET.get('members', '')
    return email_view(request, DepotForm, depot_id=depot_id, initial={
        'to_depot': not members,
        'to_members': members.split('-')
    })


@login_required
def to_area(request, area_id):
    if not request.user.member.can_contact(area_id=area_id):
        raise PermissionDenied
    members = request.GET.get('members', '')
    return email_view(request, AreaForm, area_id=area_id, initial={
        'to_area': not members,
        'to_members': members.split('-')
    })


@login_required
def to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if not request.user.member.can_contact(area_id=job.type.activityarea):
        raise PermissionDenied
    members = request.GET.get('members', '')
    return email_view(request, JobForm, job_id=job_id, initial={
        'to_job': not members,
        'to_members': members.split('-')
    })


@requires_permission_to_contact
def write(request):
    initial = dict(
        to_jobs=[request.GET.get('job')],
        to_members=request.GET.get('members', '').split('-')
    )
    return email_view(request, EmailForm, initial)


def email_view(request, form_class: type[BaseForm] = EmailForm, initial=None, **kwargs):
    user = request.user
    member = user.member
    templates = kwargs.get('templates', request.user.has_perm('juntagrico.can_load_templates'))
    attachments = kwargs.get('attachments', request.user.has_perm('juntagrico.can_email_attachments'))

    # limit available areas and depots if user can't send emails in general
    depots = areas = None
    if not user.has_perm('juntagrico.can_send_mails'):
        depots = Depot.objects.none()
        if user.has_perm('juntagrico.is_depot_admin'):
            depots = kwargs.get('depots', member.depot_set.all())  # coordinated depots
        areas = kwargs.get('areas', member.coordinated_areas.filter(coordinator_access__can_contact_member=True))

    kwargs.update(dict(
        initial=initial,
        depots=depots,
        areas=areas,
        templates=templates,
        attachments=attachments
    ))

    if request.method == 'POST':
        form = form_class(member, data=request.POST, files=request.FILES, **kwargs)
        if form.is_valid():
            try:
                if form.send():
                    messages.success(request, _('E-Mail(s) gesendet'))
                    return redirect('email-sent')
                messages.error(request, _('E-Mail(s) konnten nicht gesendet werden.'))
            except SMTPException as e:
                messages.error(request, _('Fehler beim Senden des E-Mails: ') + str(e))
    else:
        form = form_class(member, **kwargs)

    return render(request, 'juntagrico/email/write.html', {
        'form': form,
    })


@requires_permission_to_contact
def sent(request):
    # show empty page with only success message
    return render(request, 'base.html')


@permission_required('juntagrico.can_load_templates')
def get_template(request, template_id):
    renderdict = {}
    template = MailTemplate.objects.get(id=template_id)
    try:
        exec(template.code)
    except SyntaxError as e:
        return HttpResponseServerError(str(e))
    t = Template(template.template)
    c = Context(renderdict)
    result = t.render(c)
    return HttpResponse(result)
