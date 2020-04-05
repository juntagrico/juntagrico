import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.module_loading import import_string

from juntagrico.config import Config
from juntagrico.util.mailer import filter_whitelist_emails

log = logging.getLogger('juntagrico.mailer')


def prepare_email(*args, **kwargs):
    kwargs.setdefault("from_email", Config.info_email())
    return EmailMultiAlternatives(*args, **kwargs)


def send_to(email, to, **kwargs):
    to = [to] if isinstance(to, str) else to
    email.to = to
    for key, value in kwargs.items():
        setattr(email, key, value)
    send(email)


def send(email):
    # only send to whitelisted emails in dev
    email.to = filter_whitelist_emails(email.to)
    email.cc = filter_whitelist_emails(email.cc)
    email.bcc = filter_whitelist_emails(email.bcc)
    # send with juntagrico mailer or custom mailer
    log.info(('Mail sent to ' + ', '.join(email.recipients()) + (', on whitelist' if settings.DEBUG else '')))
    mailer = import_string(Config.default_mailer())
    mailer.send(email)


def attach_html(email, html):
    email.attach_alternative(html, 'text/html')


def attach_files(email, files):
    for file in files or []:
        email.attach(file.name, file.read())


def attach_ics(email, ics):
    email.attach(ics.name, ics.content)


def get_thread_id(uid):
    return f'<{uid}@{Config.server_url()}>'


def start_thread(email, uid):
    # Tested and working on Thunderbird, Gmail and K9-Mail
    # Does not work on any Microsoft E-Mail client:
    #   Tried this without success https://bugzilla.mozilla.org/show_bug.cgi?id=411601
    # Apples not tested
    email.extra_headers.update({'Message-ID': get_thread_id(uid)})


def continue_thread(email, uid):
    tid = get_thread_id(uid)
    email.extra_headers.update({'References': tid, 'In-Reply-To': tid})
