from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import get_language
from django.utils.translation import ngettext, gettext as _
from django_select2.views import AutoResponseView

from juntagrico.forms.email import EmailForm, EmailRecipientsForm
from juntagrico.util.settings import tinymce_lang

from juntagrico.entity.mailing import MailTemplate
from juntagrico.entity.member import Member


class InternalSelect2View(LoginRequiredMixin, AutoResponseView):
    """Limit access to autocomplete (select2) to logged-in users
    """
    pass


@permission_required('juntagrico.can_send_mails')
def to_member(request, member_id, mail_url='mail-send'):
    renderdict = {
        'recipients': get_object_or_404(Member, id=member_id).email,
        'recipients_count': 1,
        'mail_url': mail_url,
        'email': request.user.member.email,
        'templates': MailTemplate.objects.all(),
        'richtext_language': tinymce_lang(get_language()),
    }
    return render(request, 'mail_sender.html', renderdict)


@login_required
def count_recipients(request):
    form = EmailRecipientsForm(request.user.member, request.GET)
    if form.is_valid():
        if count := form.count_recipients():
            return HttpResponse(ngettext(
                'An {} Person senden',
                'An {} Personen senden',
                count
            ).format(count))
    return HttpResponse(_('Senden'))


@login_required
def write(request):
    member = request.user.member
    # TODO: try to remember the context of the request. If members were selected in the area list, include the
    #       footer that says "you receive this email because you are in the area ..."
    #       If all members or area/depot are selected, make sure to prefill the to_areas and to_depots field
    #       and not the to_members field.
    initial = dict(
        to_members=request.GET.get('members', '').split('-')
    )

    features = dict(
        template=request.user.has_perm('juntagrico.can_load_templates'),
        # TODO: using this permission from the future
        attachment=request.user.has_perm('juntagrico.can_email_attachments'),
    )

    if request.method == 'POST':
        form = EmailForm(member, features, request.POST, request.FILES, initial=initial)
        if form.is_valid():
            if form.send():
                messages.success(request, _('E-Mail(s) gesendet'))
                return redirect('email-write')  # TODO: redirect back to previous page ideally.
            messages.error(request, _('E-Mail(s) konnten nicht gesendet werden.'))
    else:
        form = EmailForm(member, features, initial=initial)

    return render(request, 'juntagrico/email/write.html', {
        'form': form,
    })
