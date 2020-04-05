import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.module_loading import import_string

from juntagrico.config import Config
from juntagrico.util.mailer import filter_whitelist_emails

log = logging.getLogger('juntagrico.mailer')


def chainable(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        return args[-1]
    return wrapper


def prepare_email(*args, **kwargs):
    kwargs.setdefault("from_email", Config.info_email())
    return EmailMultiAlternatives(*args, **kwargs)


def send_to(to, email, **kwargs):
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


@chainable
def attach_html(html, email):
    email.attach_alternative(html, 'text/html')


@chainable
def attach_files(files, email):
    for file in files or []:
        email.attach(file.name, file.read())


@chainable
def attach_ics(ics, email):
    email.attach(ics.name, ics.content)


def get_thread_id(uid):
    return f'<{uid}@{Config.server_url()}>'


@chainable
def start_thread(uid, email):
    # Tested and working on Thunderbird, Gmail and K9-Mail
    # Does not work on any Microsoft E-Mail client:
    #   Tried this without success https://bugzilla.mozilla.org/show_bug.cgi?id=411601
    # Apples not tested
    email.extra_headers.update({'Message-ID': get_thread_id(uid)})


@chainable
def continue_thread(uid, email):
    tid = get_thread_id(uid)
    email.extra_headers.update({'References': tid, 'In-Reply-To': tid})
