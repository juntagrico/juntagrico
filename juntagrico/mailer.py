import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.util.mailer import get_emails_by_permission, base_dict, get_email_content, filter_whitelist_emails
from juntagrico.util.ical import generate_ical_for_job
from juntagrico.util.organisation_name import enriched_organisation

log = logging.getLogger('juntagrico.mailer')


def organisation_subject(subject):
    return Config.organisation_name() + ' - ' + subject


class Email(EmailMultiAlternatives):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("from_email", Config.info_email())
        super().__init__(*args, **kwargs)

    def send_to(self, to=None, **kwargs):
        to = [to] if isinstance(to, str) else to
        self.to = to or self.to
        # allow overriding of settings
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.send()

    def send(self, fail_silently=False):
        # only send to whitelisted emails in dev
        self.to = filter_whitelist_emails(self.to)
        self.cc = filter_whitelist_emails(self.cc)
        self.bcc = filter_whitelist_emails(self.bcc)
        # send with juntagrico mailer or custom mailer
        log.info(('Mail sent to ' + ', '.join(self.recipients()) + (', on whitelist' if settings.DEBUG else '')))
        mailer = import_string(Config.default_mailer())
        mailer.send(super())

    def attach_html(self, html):
        self.attach_alternative(html, 'text/html')
        return self

    def attach_files(self, files):
        for file in files or []:
            self.attach(file.name, file.read())
        return self

    def attach_ics(self, ics):
        self.attach(ics.name, ics.content)
        return self

    @staticmethod
    def _get_thread_id(uid):
        return f'<{uid}@{Config.server_url()}>'

    def start_thread(self, uid):
        # Tested and working on Thunderbird, Gmail and K9-Mail
        # Does not work on any Microsoft E-Mail client:
        #   Tried this without success https://bugzilla.mozilla.org/show_bug.cgi?id=411601
        # Apples not tested
        self.extra_headers.update({'Message-ID': self._get_thread_id(uid)})
        return self

    def continue_thread(self, uid):
        tid = self._get_thread_id(uid)
        self.extra_headers.update({'References': tid, 'In-Reply-To': tid})
        return self


class FormEmails:
    """
    Form emails
    """
    @staticmethod
    def contact(subject, message, member, copy_to_member):
        subject = _('Anfrage per {0}:').format(Config.adminportal_name()) + subject
        email = Email(subject, message)
        email.send_to(Config.info_email(), reply_to=member.email)
        if copy_to_member:
            email.send_to(member.email)

    @staticmethod
    def contact_member(subject, message, member, contact_member, copy_to_member, files):
        subject = _('Nachricht per {0}:').format(Config.adminportal_name()) + subject
        email = Email(subject, message, reply_to=member.email).attach_files(files)
        email.send_to(contact_member.email)
        if copy_to_member:
            email.send_to(member.email)

    @staticmethod
    def internal(subject, message, text_message, emails, files, sender):
        htmld = base_dict({
            'mail_template': Config.mail_template,
            'subject': subject,
            'content': message
        })
        textd = base_dict({
            'subject': subject,
            'content': text_message
        })
        text_content = get_template('mails/form/filtered_mail.txt').render(textd)
        html_content = get_template('mails/form/filtered_mail.html').render(htmld)
        Email(subject, text_content, bcc=emails, from_email=sender)\
            .attach_html(html_content).attach_files(files).send()


class AdminNotification:
    """
    Admin notification emails
    """
    @staticmethod
    def member_joined_activityarea(area, member):
        Email(
            organisation_subject(_('Neues Mitglied im Taetigkeitsbereich {0}').format(area.name)),
            _('Soeben hat sich {0} {1} in den Taetigkeitsbereich {2} eingetragen').format(
                member.first_name, member.last_name, area.name
            ),
        ).send_to(area.get_email())

    @staticmethod
    def member_left_activityarea(area, member):
        Email(
            organisation_subject(_('Mitglied verlässt Taetigkeitsbereich {0}').format(area.name)),
            _('Soeben hat sich {0} {1} aus dem Taetigkeitsbereich {2} ausgetragen. '
              'Bitte lösche seine Kontaktdaten aus allen deinen Privaten Adressbüchern').format(
                member.first_name, member.last_name, area.name
            ),
        ).send_to(area.get_email())

    @staticmethod
    def subscription_created(subscription):
        Email(
            organisation_subject(_('Neue/r/s {} erstellt').format(Config.vocabulary('subscription'))),
            get_email_content('n_sub', base_dict(locals())),
            bcc=get_emails_by_permission('notified_on_subscription_creation')
        ).send()

    @staticmethod
    def subscription_canceled(subscription, message):
        Email(
            organisation_subject(_('{} gekündigt').format(Config.vocabulary('subscription'))),
            get_email_content('s_canceled', base_dict(locals())),
            bcc=get_emails_by_permission('notified_on_subscription_cancellation')
        ).send()

    @staticmethod
    def share_created(share):
        Email(
            organisation_subject(_('Neue/r/s {} erstellt').format(Config.vocabulary('share'))),
            get_email_content('a_share_created', base_dict(locals())),
            bcc=get_emails_by_permission('notified_on_share_creation')
        ).send()

    @staticmethod
    def member_created(member):
        Email(
            organisation_subject(_('Neue/r/s {}').format(Config.vocabulary('member_type'))),
            get_email_content('a_member_created', base_dict(locals())),
            bcc=get_emails_by_permission('notified_on_member_creation')
        ).send()

    @staticmethod
    def member_canceled(member, end_date, message):
        Email(
            organisation_subject(_('{} gekündigt').format(Config.vocabulary('member_type'))),
            get_email_content('m_canceled', base_dict(locals())),
            bcc=get_emails_by_permission('notified_on_member_cancellation')
        ).send()


class MemberNotification:
    """
    Member notification emails
    """
    @staticmethod
    def welcome(member, password):
        Email(
            _('Willkommen bei {0}').format(enriched_organisation('D')),
            get_email_content('welcome', base_dict(locals())),
        ).send_to(member.email)

    @staticmethod
    def welcome_co_member(co_member, password, new_shares, new=True):
        # sends either welcome mail or just information mail to new/added co-member
        Email(
            _('Willkommen bei {0}').format(enriched_organisation('D')),
            get_email_content('co_welcome' if new else 'co_added', base_dict(locals())),
        ).send_to(co_member.email)

    @staticmethod
    def shares_created(member, shares):
        Email(
            organisation_subject(_('Dein neuer Anteilschein')),
            get_email_content('s_created', base_dict(locals())),
        ).send_to(member.email)

    @staticmethod
    def email_confirmation(member):
        d = {'hash': member.get_hash()}
        Email(
            organisation_subject(_('E-Mail-Adresse bestätigen')),
            get_email_content('confirm', base_dict(d)),
        ).send_to(member.email)

    @staticmethod
    def reset_password(email, password):
        Email(
            organisation_subject(_('Dein neues Passwort')),
            get_email_content('password', base_dict(locals())),
        ).send_to(email)

    @staticmethod
    def depot_changed(emails, depot):
        Email(
            organisation_subject(_('{} geändert').format(Config.vocabulary('depot'))),
            get_email_content('d_changed', base_dict(locals())),
            bcc=emails
        ).send()

    @staticmethod
    def co_member_left_subscription(primary_member, co_member, message):
        Email(
            organisation_subject(_('Austritt aus {}').format(Config.vocabulary('subscription'))),
            get_email_content('m_left_subscription', base_dict(locals())),
            primary_member.email
        )

    @staticmethod
    def job_signup(email, job):
        Email(
            organisation_subject(_('Für Einsatz angemeldet')),
            get_email_content('j_signup', base_dict(locals()))
        ).attach_ics(generate_ical_for_job(job)).start_thread(repr(job)).send_to(email)

    @staticmethod
    def job_reminder(emails, job, participants):
        contact = job.type.activityarea.coordinator.get_name() + ': ' + job.type.activityarea.contact()
        Email(
            organisation_subject(_('Einsatz-Erinnerung')),
            get_email_content('j_reminder', base_dict(locals())),
            bcc=emails
        ).attach_ics(generate_ical_for_job(job)).continue_thread(repr(job)).send()

    @staticmethod
    def job_time_changed(emails, job):
        Email(
            organisation_subject(_('Einsatz-Zeit geändert')),
            get_email_content('j_changed', base_dict(locals())),
            bcc=emails
        ).attach_ics(generate_ical_for_job(job)).continue_thread(repr(job)).send()

    @staticmethod
    def job_canceled(emails, job):
        Email(
            organisation_subject(_('Einsatz abgesagt')),
            get_email_content('j_canceled', base_dict(locals())),
            bcc=emails
        ).attach_ics(generate_ical_for_job(job)).continue_thread(repr(job)).send()
