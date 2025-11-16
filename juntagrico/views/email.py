from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ngettext, gettext as _
from django_select2.views import AutoResponseView

from juntagrico.forms.email import EmailForm, RecipientsForm, DepotForm, BaseForm, DepotRecipientsForm

class InternalSelect2View(LoginRequiredMixin, AutoResponseView):
    """Limit access to autocomplete (select2) to logged-in users
    """
    pass


@login_required
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


@login_required
def count_depot_recipients(request, depot_id):
    form = DepotRecipientsForm(request.user.member, {'depot': depot_id}, data=request.GET)
    return count_recipients(request, form)


@login_required
def to_member(request, member_id):
    # TODO: Check if request.user.member can contact member_id
    return email_view(request, EmailForm, {
        'recipients': ['to_members', 'copy']
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


@login_required
def write(request):
    # TODO: limit access
    initial = dict(
        to_jobs=[request.GET.get('job')],
        to_members=request.GET.get('members', '').split('-')
    )
    return email_view(request, EmailForm, initial=initial)


def email_view(request, form_class: type(BaseForm) = EmailForm, features=None, initial=None):
    member = request.user.member
    features = features or {}
    features.setdefault('template', request.user.has_perm('juntagrico.can_load_templates'))
    # TODO: using this permission from the future
    features.setdefault('attachment', request.user.has_perm('juntagrico.can_email_attachments'))

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