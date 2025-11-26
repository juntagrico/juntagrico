from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.template import Template, Context
from django.utils.translation import ngettext, gettext as _
from django_select2.views import AutoResponseView

from juntagrico.entity.depot import Depot
from juntagrico.entity.mailing import MailTemplate
from juntagrico.forms.email import EmailForm, RecipientsForm, DepotForm, BaseForm, DepotRecipientsForm, AreaForm, \
    AreaRecipientsForm, JobForm, JobRecipientsForm
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
    form = DepotRecipientsForm(request.user.member, {'depot': depot_id}, data=request.GET)
    return count_recipients(request, form)


@requires_permission_to_contact
def count_area_recipients(request, area_id):
    form = AreaRecipientsForm(request.user.member, {'area': area_id}, data=request.GET)
    return count_recipients(request, form)


@requires_permission_to_contact
def count_job_recipients(request, job_id):
    form = JobRecipientsForm(request.user.member, {'job': job_id}, data=request.GET)
    return count_recipients(request, form)


@login_required
def to_member(request, member_id):
    # TODO: Check if request.user.member can contact member_id
    return email_view(request, EmailForm, {
        'recipients': {
            'fields': ['to_members', 'copy']
        }
    }, {
        'to_members': [member_id]
    })


@permission_required('juntagrico.is_depot_admin')
def to_depot(request, depot_id):
    # TODO: include an email footer that says "you receive this email because you are in the depot ..."
    members = request.GET.get('members', '')
    return email_view(request, DepotForm, {
        'recipients': {'depot': depot_id}
    }, {
        'to_depot': not members,
        'to_members': members.split('-')
    })


@requires_permission_to_contact
def to_area(request, area_id):
    # TODO: include an email footer that says "you receive this email because you are in the area ..."
    members = request.GET.get('members', '')
    return email_view(request, AreaForm, {
        'recipients': {'area': area_id}
    }, {
        'to_area': not members,
        'to_members': members.split('-')
    })


@requires_permission_to_contact
def to_job(request, job_id):
    # TODO: include an email footer that says "you receive this email because you are in the job ..."
    members = request.GET.get('members', '')
    return email_view(request, JobForm, {
        'recipients': {'job': job_id}
    }, {
        'to_job': not members,
        'to_members': members.split('-')
    })


@requires_permission_to_contact
def write(request):
    initial = dict(
        to_jobs=[request.GET.get('job')],
        to_members=request.GET.get('members', '').split('-')
    )
    return email_view(request, EmailForm, initial=initial)


def email_view(request, form_class: type(BaseForm) = EmailForm, features=None, initial=None):
    user = request.user
    member = user.member
    features = features or {}
    features.setdefault('template', request.user.has_perm('juntagrico.can_load_templates'))
    features.setdefault('attachment', request.user.has_perm('juntagrico.can_email_attachments'))

    # limit available areas and depots if user can't send emails in general
    if not user.has_perm('juntagrico.can_send_mails'):
        depots = Depot.objects.none()
        if user.has_perm('juntagrico.is_depot_admin'):
            depots = features.setdefault('depots', Depot.objects.filter(contact=member))
        features.setdefault('recipients', {
            'areas': member.coordinated_areas.filter(coordinator_access__can_contact_member=True),
            'depots': depots,
        })

    if request.method == 'POST':
        form = form_class(member, features, request.POST, request.FILES, initial=initial)
        if form.is_valid():
            try:
                if form.send():
                    messages.success(request, _('E-Mail(s) gesendet'))
                    return redirect('.')  # TODO: redirect back to previous page ideally.
                messages.error(request, _('E-Mail(s) konnten nicht gesendet werden.'))
            except SMTPException as e:
                messages.error(request, _('Fehler beim Senden des E-Mails: ') + str(e))
    else:
        form = form_class(member, features, initial=initial)

    return render(request, 'juntagrico/email/write.html', {
        'form': form,
    })


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
