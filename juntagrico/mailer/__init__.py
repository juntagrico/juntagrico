import logging
import re

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.db.models import QuerySet
from django.template.loader import get_template
from django.utils import translation

from juntagrico.config import Config
from juntagrico.context_processors import Vocabulary
from juntagrico.util.decorators import chainable

log = logging.getLogger('juntagrico.mailer')


def base_dict(add=None):
    """ Deprecated! Use EmailBuilder instead
    """
    add = add or {}
    add['serverurl'] = Config.url_protocol() + Site.objects.get_current().domain
    add['vocabulary'] = Vocabulary()
    return add


def get_email_content(template, template_dict=None):
    """ Deprecated! Use EmailBuilder instead
    """
    template_dict = template_dict or {}
    return get_template(Config.emails(template)).render(template_dict)


def get_emails_by_permission(permission_code):
    """ Deprecated! Use EmailBuilder instead
    Get all email addresses of members by permission of user
    """
    from juntagrico.dao.memberdao import MemberDao
    emails = MemberDao.members_by_permission(permission_code).values_list('email', flat=True)
    return emails


def requires_someone_with_perm(perm):
    """ Deprecated! Use EmailBuilder instead
    """
    def skip_decorator(func):
        def wrapper(*args, **kwargs):
            emails = get_emails_by_permission(perm)
            if len(emails) > 0:
                kwargs['emails'] = emails
                return func(*args, **kwargs)
        return wrapper
    return skip_decorator


def organisation_subject(subject):
    return Config.organisation_name() + ' - ' + subject


def get_thread_id(obj):
    return f'<{type(obj).__name__}{obj.id}@{Site.objects.get_current().domain}>'


def recipients_by_permission(permission_code):
    from juntagrico.entity.member import Member
    return Member.objects.by_permission(permission_code)


def trim_newlines(text):
    return re.sub(r'((?:\r?\n|\r){,2})(?:\r?\n|\r)*', r'\1', text).strip()


class EmailBuilder:
    def __init__(self, recipients, subject, template, context=None, from_email=None, reply_to=None):
        """
        :param recipients: a member, queryset/list/tuple of members or a permission string defining who to send the email to.
                           Also accepts list of tuples with (email, member) where member can be None.
        :param subject: the subject of the email as a lazy translation string
        :param template: the template to use for the body of the email. Path, EMAILS setting key, 'admin' or 'member'
        :param context: a dict of context for the email or a string. In case of string it is passed to the template as 'message'
        :param from_email: email to use as sender. String or CONTACTS setting key. default: general contact.
        """
        if recipients is None:
            self.recipients = []
        elif isinstance(recipients, str):
            self.recipients = recipients_by_permission(recipients)
        elif isinstance(recipients, (QuerySet, list, tuple)):
            self.recipients = recipients
        else:
            self.recipients = [recipients]
        self.subject = subject
        self.template = template
        self.context = context or {}
        self.from_email = from_email
        self.reply_to = reply_to
        self.attachments = []
        self.headers = {}

    def send(self):
        if not self.recipients:
            return 0

        from_email = Config.contacts(self.from_email, self.from_email) or Config.contacts('general')

        context = self.context
        if not isinstance(context, dict):
            context = {'message': context}
        context['vocabulary'] = Vocabulary()
        context['server_url'] = Config.url_protocol() + Site.objects.get_current().domain
        context['serverurl'] = context['server_url']  # backwards compatibility

        if self.template in ('admin', 'member'):
            template = f'juntagrico/mails/{self.template}/base.txt'
        else:
            template = Config.emails(self.template, self.template)
        template = get_template(template)

        count = 0
        with mail.get_connection() as connection:
            for recipient in self.recipients:
                if isinstance(recipient, (list, tuple)):
                    email, recipient = recipient
                else:
                    email = recipient.email

                # TODO: activate language of recipient here
                if language := getattr(settings, 'EMAIL_LANGUAGE', None):
                    translation.activate(language)
                count += EmailMultiAlternatives(
                    subject=organisation_subject(self.subject),
                    body=trim_newlines(template.render(context | {'recipient': recipient})),
                    from_email=from_email,
                    to=[email],
                    connection=connection,
                    attachments=[a() if callable(a) else a for a in self.attachments],
                    headers=self.headers,
                    reply_to=self.reply_to,
                ).send()
                translation.deactivate()
        return count

    @chainable
    def attach(self, attachment):
        self.attachments.append(attachment)

    @chainable
    def start_thread(self, uid):
        # Tested and working on Thunderbird, Gmail and K9-Mail
        # Does not work on any Microsoft E-Mail client:
        #   Tried this without success https://bugzilla.mozilla.org/show_bug.cgi?id=411601
        # Apples not tested
        self.headers.update({'Message-ID': get_thread_id(uid)})

    @chainable
    def continue_thread(self, uid):
        tid = get_thread_id(uid)
        self.headers.update({'References': tid, 'In-Reply-To': tid})


class EmailSender:
    """Deprecated! Use EmailBuilder instead
    """

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
