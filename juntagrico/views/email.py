from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language

from juntagrico.util.settings import tinymce_lang

from juntagrico.entity.mailing import MailTemplate
from juntagrico.entity.member import Member


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
