import logging
import re

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from juntagrico.config import Config
from juntagrico.util.decorators import chainable

log = logging.getLogger('juntagrico.mailer')


def base_dict(add=None):
    add = add or {}
    add['serverurl'] = Config.url_protocol() + Site.objects.get_current().domain
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


def requires_someone_with_perm(perm):
    def skip_decorator(func):
        def wrapper(*args, **kwargs):
            emails = get_emails_by_permission(perm)
            if len(emails) > 0:
                kwargs['emails'] = emails
                return func(*args, **kwargs)
        return wrapper
    return skip_decorator


def filter_whitelist_emails(to_emails):
    if settings.DEBUG:
        ok_mails = [x for x in to_emails if any(re.match(wle, x) for wle in settings.WHITELIST_EMAILS)]
        not_send = [x for x in to_emails if x not in ok_mails]
        log.info(('Mail not sent to: ' + ', '.join(not_send) + ' not in whitelist'))
        return ok_mails
    else:
        return to_emails


def organisation_subject(subject):
    return Config.organisation_name() + ' - ' + subject


def get_thread_id(obj):
    return f'<{type(obj).__name__}{obj.id}@{Site.objects.get_current().domain}>'


class EmailSender:

    @staticmethod
    def get_sender(*args, **kwargs):
        kwargs.setdefault("from_email", Config.contacts('general'))
        email = EmailMultiAlternatives(*args, **kwargs)
        return EmailSender(email)

    @staticmethod
    def get_sender_for_contact(contact, *args, **kwargs):
        return EmailSender.get_sender(*args, from_email=Config.contacts(contact), **kwargs)

    @staticmethod
    def get_sender_from_email(email):
        return EmailSender(email)

    def __init__(self, email):
        self.email = email
        self.email.body = self.trim_newlines(self.email.body)

    @staticmethod
    def trim_newlines(text):
        return re.sub(r'((?:\r?\n|\r){,2})(?:\r?\n|\r)*', r'\1', text).strip()

    def send_to(self, to, **kwargs):
        to = [to] if isinstance(to, str) else to
        self.email.to = to
        for key, value in kwargs.items():
            setattr(self.email, key, value)
        self.send()

    def send(self):
        self.email.send()

    @chainable
    def attach_html(self, html):
        self.email.attach_alternative(html, 'text/html')

    @chainable
    def attach_files(self, files):
        for file in files or []:
            self.email.attach(file.name, file.read())

    @chainable
    def attach_ics(self, ics):
        self.email.attach(ics.name, ics.content)

    @chainable
    def start_thread(self, uid):
        # Tested and working on Thunderbird, Gmail and K9-Mail
        # Does not work on any Microsoft E-Mail client:
        #   Tried this without success https://bugzilla.mozilla.org/show_bug.cgi?id=411601
        # Apples not tested
        self.email.extra_headers.update({'Message-ID': get_thread_id(uid)})

    @chainable
    def continue_thread(self, uid):
        tid = get_thread_id(uid)
        self.email.extra_headers.update({'References': tid, 'In-Reply-To': tid})
