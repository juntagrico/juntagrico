from django.template.loader import get_template
from django.conf import settings

from juntagrico.config import Config


def base_dict(add=None):
    add = add or {}
    add['serverurl'] = 'http://' + Config.adminportal_server_url()
    return add


def get_email_content(template, template_dict=None):
    template_dict = template_dict or {}
    return get_template(Config.emails(template)).render(template_dict)


def append_attachements(request, attachements):
    index = 1
    while request.FILES.get('image-' + str(index)) is not None:
        attachements.append(request.FILES.get('image-' + str(index)))
        index += 1


def get_emails_by_permission(permission_code):
    """
    Get all email addresses of members by permission of user
    """
    from juntagrico.dao.memberdao import MemberDao
    emails = MemberDao.members_by_permission(permission_code).values_list('email', flat=True)
    return emails


def filter_whitelist_emails(to_emails):
    if settings.DEBUG:
        ok_mails = [x for x in to_emails if x in settings.WHITELIST_EMAILS]
        not_send = [x for x in to_emails if x not in settings.WHITELIST_EMAILS]
        print(('Mail not sent to: ' + ', '.join(not_send) + ' not in whitelist'))
        return ok_mails
    else:
        return to_emails
