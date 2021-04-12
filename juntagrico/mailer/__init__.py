import logging
import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.module_loading import import_string

from juntagrico.config import Config
from juntagrico.util.decorators import chainable

log = logging.getLogger('juntagrico.mailer')


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
    return f'<{type(obj).__name__}{obj.id}@{Config.server_url()}>'


class EmailSender:

    @staticmethod
    def get_sender(*args, **kwargs):
        kwargs.setdefault("from_email", Config.info_email())
        email = EmailMultiAlternatives(*args, **kwargs)
        return EmailSender(email)

    @staticmethod
    def get_sender_from_email(email):
        return EmailSender(email)

    def __init__(self, email):
        self.email = email

    def send_to(self, to, **kwargs):
        to = [to] if isinstance(to, str) else to
        self.email.to = to
        for key, value in kwargs.items():
            setattr(self.email, key, value)
        self.send()

    def send(self):
        # only send to whitelisted emails in dev
        self.email.to = filter_whitelist_emails(self.email.to)
        self.email.cc = filter_whitelist_emails(self.email.cc)
        self.email.bcc = filter_whitelist_emails(self.email.bcc)
        # apply from filter
        if not re.match(Config.from_filter('filter_expression'), self.email.from_email):
            reply_to = self.email.reply_to or [self.email.from_email]
            self.email.from_email = Config.from_filter('replacement_from')
            self.email.reply_to = reply_to
        # send with juntagrico mailer or custom mailer
        log.info(('Mail sent to ' + ', '.join(self.email.recipients()) + (', on whitelist' if settings.DEBUG else '')))
        mailer = import_string(Config.default_mailer())
        mailer.send(self.email)

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
