import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer.emailsender import prepare_email, send_to, send, attach_files, attach_html, attach_ics, \
    start_thread, continue_thread
from juntagrico.util.mailer import get_emails_by_permission, base_dict, get_email_content, filter_whitelist_emails
from juntagrico.util.ical import generate_ical_for_job
from juntagrico.util.organisation_name import enriched_organisation

log = logging.getLogger('juntagrico.mailer')


def chainable(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        return args[0]
    return wrapper

def organisation_subject(subject):
    return Config.organisation_name() + ' - ' + subject





class FormEmails:
    """
    Form emails
    """
    @staticmethod
    def contact(subject, message, member, copy_to_member):
        subject = _('Anfrage per {0}:').format(Config.adminportal_name()) + subject
        email = prepare_email(subject, message)
        send_to(email, Config.info_email(), reply_to=member.email)
        if copy_to_member:
            send_to(email, member.email)

    @staticmethod
    def contact_member(subject, message, member, contact_member, copy_to_member, files):
        subject = _('Nachricht per {0}:').format(Config.adminportal_name()) + subject
        email =prepare_email(subject, message, reply_to=[member.email])
        attach_files(email, files)
        send_to(email, contact_member.email)
        if copy_to_member:
            send_to(email, member.email)

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
        email = prepare_email(subject, text_content, bcc=emails, from_email=sender)
        attach_html(email, html_content)
        attach_files(email, files)
        send(email)


class AdminNotification:
    """
    Admin notification emails
    """
    @staticmethod
    def member_joined_activityarea(area, member):
        email = prepare_email(
            organisation_subject(_('Neues Mitglied im Taetigkeitsbereich {0}').format(area.name)),
            _('Soeben hat sich {0} {1} in den Taetigkeitsbereich {2} eingetragen').format(
                member.first_name, member.last_name, area.name
            )
        )
        send_to(email, area.get_email())

    @staticmethod
    def member_left_activityarea(area, member):
        email = prepare_email(
            organisation_subject(_('Mitglied verlässt Taetigkeitsbereich {0}').format(area.name)),
            _('Soeben hat sich {0} {1} aus dem Taetigkeitsbereich {2} ausgetragen. '
              'Bitte lösche seine Kontaktdaten aus allen deinen Privaten Adressbüchern').format(
                member.first_name, member.last_name, area.name
            ),
        )
        send_to(email, area.get_email())

    @staticmethod
    def subscription_created(subscription):
        email= prepare_email(
            organisation_subject(_('Neue/r/s {} erstellt').format(Config.vocabulary('subscription'))),
            get_email_content('n_sub', base_dict(locals())),
            bcc=get_emails_by_permission('notified_on_subscription_creation')
        )
        send(email)

    @staticmethod
    def subscription_canceled(subscription, message):
        email = prepare_email(
            organisation_subject(_('{} gekündigt').format(Config.vocabulary('subscription'))),
            get_email_content('s_canceled', base_dict(locals())),
            bcc=get_emails_by_permission('notified_on_subscription_cancellation')
        )
        send(email)

    @staticmethod
    def share_created(share):
        email = prepare_email(
            organisation_subject(_('Neue/r/s {} erstellt').format(Config.vocabulary('share'))),
            get_email_content('a_share_created', base_dict(locals())),
            bcc=get_emails_by_permission('notified_on_share_creation')
        )
        send(email)

    @staticmethod
    def member_created(member):
        email = prepare_email(
            organisation_subject(_('Neue/r/s {}').format(Config.vocabulary('member_type'))),
            get_email_content('a_member_created', base_dict(locals())),
            bcc=get_emails_by_permission('notified_on_member_creation')
        )
        send(email)

    @staticmethod
    def member_canceled(member, end_date, message):
        email = prepare_email(
            organisation_subject(_('{} gekündigt').format(Config.vocabulary('member_type'))),
            get_email_content('m_canceled', base_dict(locals())),
            bcc=get_emails_by_permission('notified_on_member_cancellation')
        )
        send(email)


class MemberNotification:
    """
    Member notification emails
    """
    @staticmethod
    def welcome(member, password):
        email = prepare_email(
            _('Willkommen bei {0}').format(enriched_organisation('D')),
            get_email_content('welcome', base_dict(locals())),
        )
        send_to(email, member.email)

    @staticmethod
    def welcome_co_member(co_member, password, new_shares, new=True):
        # sends either welcome mail or just information mail to new/added co-member
        email = prepare_email(
            _('Willkommen bei {0}').format(enriched_organisation('D')),
            get_email_content('co_welcome' if new else 'co_added', base_dict(locals())),
        )
        send_to(email, co_member.email)

    @staticmethod
    def shares_created(member, shares):
        email = prepare_email(
            organisation_subject(_('Dein neuer Anteilschein')),
            get_email_content('s_created', base_dict(locals())),
        )
        send_to(email, member.email)

    @staticmethod
    def email_confirmation(member):
        d = {'hash': member.get_hash()}
        email= prepare_email(
            organisation_subject(_('E-Mail-Adresse bestätigen')),
            get_email_content('confirm', base_dict(d)),
        )
        send_to(email, member.email)

    @staticmethod
    def reset_password(email_adr, password):
        email = prepare_email(
            organisation_subject(_('Dein neues Passwort')),
            get_email_content('password', base_dict(locals())),
        )
        send_to(email, email_adr)

    @staticmethod
    def depot_changed(emails, depot):
        email = prepare_email(
            organisation_subject(_('{} geändert').format(Config.vocabulary('depot'))),
            get_email_content('d_changed', base_dict(locals())),
            bcc=emails
        )
        send(email)

    @staticmethod
    def co_member_left_subscription(primary_member, co_member, message):
        email = prepare_email(
            organisation_subject(_('Austritt aus {}').format(Config.vocabulary('subscription'))),
            get_email_content('m_left_subscription', base_dict(locals())),
            to=[primary_member.email]
        )
        send(email)

    @staticmethod
    def job_signup(email_adr, job):
        email = prepare_email(
            organisation_subject(_('Für Einsatz angemeldet')),
            get_email_content('j_signup', base_dict(locals()))
        )
        start_thread(email, repr(job))
        attach_ics(email, generate_ical_for_job(job))
        send_to(email, email_adr)

    @staticmethod
    def job_reminder(emails, job, participants):
        contact = job.type.activityarea.coordinator.get_name() + ': ' + job.type.activityarea.contact()
        email = prepare_email(
            organisation_subject(_('Einsatz-Erinnerung')),
            get_email_content('j_reminder', base_dict(locals())),
            bcc=emails
        )
        attach_ics(email, generate_ical_for_job(job))
        continue_thread(email, repr(job))
        send(email)

    @staticmethod
    def job_time_changed(emails, job):
        email = prepare_email(
            organisation_subject(_('Einsatz-Zeit geändert')),
            get_email_content('j_changed', base_dict(locals())),
            bcc=emails
        )
        attach_ics(email, generate_ical_for_job(job))
        continue_thread(email, repr(job))
        send(email)

    @staticmethod
    def job_canceled(emails, job):
        email = prepare_email(
            organisation_subject(_('Einsatz abgesagt')),
            get_email_content('j_canceled', base_dict(locals())),
            bcc=emails
        )
        continue_thread(email, repr(job))
        send(email)
