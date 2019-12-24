from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.util.mailer import get_emails_by_permission, base_dict, get_email_content, filter_whitelist_emails
from juntagrico.util.organisation_name import enriched_organisation


def organisation_subject(subject):
    return Config.organisation_name() + ' - ' + subject


# sends mail only to specified email-addresses if dev mode
def send_mail(subject, message, to_emails, from_email=None, reply_to_email=None, html_message=None, attachments=None):
    to_emails = [to_emails] if isinstance(to_emails, str) else to_emails
    ok_mails = filter_whitelist_emails(to_emails)
    from_email = from_email or Config.info_email()
    if len(ok_mails) > 0:
        kwargs = {'bcc': ok_mails}
        if reply_to_email is not None:
            kwargs['reply_to'] = [reply_to_email]
        msg = EmailMultiAlternatives(subject, message, from_email, **kwargs)
        if html_message is not None:
            msg.attach_alternative(html_message, 'text/html')
        if attachments is None:
            attachments = []
        for attachment in attachments:
            msg.attach(attachment.name, attachment.read())
        print(('Mail sent to ' + ', '.join(ok_mails) + (', on whitelist' if settings.DEBUG else '')))
        mailer = import_string(Config.default_mailer())
        mailer.send(msg)


class FormEmails:
    """
    Form emails
    """
    @staticmethod
    def contact(subject, message, member, copy_to_member):
        subject = _('Anfrage per {0}:').format(Config.adminportal_name()) + subject
        send_mail(subject, message, Config.info_email(), reply_to_email=member.email)
        if copy_to_member:
            send_mail(subject, message, member.email)

    @staticmethod
    def contact_member(subject, message, member, contact_member, copy_to_member, attachments):
        subject = _('Nachricht per {0}:').format(Config.adminportal_name()) + subject
        send_mail(subject, message, contact_member.email, reply_to_email=member.email, attachments=attachments)
        if copy_to_member:
            send_mail(subject, message, member.email, reply_to_email=member.email, attachments=attachments)

    @staticmethod
    def internal(subject, message, text_message, emails, attachments, sender):
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
        send_mail(subject, text_content, emails, sender, html_message=html_content, attachments=attachments)


class AdminNotification:
    """
    Admin notification emails
    """
    @staticmethod
    def member_joined_activityarea(area, member):
        send_mail(
            organisation_subject(_('Neues Mitglied im Taetigkeitsbereich {0}').format(area.name)),
            _('Soeben hat sich {0} {1} in den Taetigkeitsbereich {2} eingetragen').format(
                member.first_name, member.last_name, area.name
            ),
            area.get_email()
        )

    @staticmethod
    def member_left_activityarea(area, member):
        send_mail(
            organisation_subject(_('Mitglied verlässt Taetigkeitsbereich {0}').format(area.name)),
            _('Soeben hat sich {0} {1} aus dem Taetigkeitsbereich {2} ausgetragen. '
              'Bitte lösche seine Kontaktdaten aus allen deinen Privaten Adressbüchern').format(
                member.first_name, member.last_name, area.name
            ),
            area.get_email()
        )

    @staticmethod
    def subscription_created(subscription):
        send_mail(
            organisation_subject(_('Neue/r/s {} erstellt').format(Config.vocabulary('subscription'))),
            get_email_content('n_sub', base_dict(locals())),
            get_emails_by_permission('notified_on_subscription_creation')
        )

    @staticmethod
    def subscription_canceled(subscription, message):
        send_mail(
            organisation_subject(_('{} gekündigt').format(Config.vocabulary('subscription'))),
            get_email_content('s_canceled', base_dict(locals())),
            get_emails_by_permission('notified_on_subscription_cancellation')
        )

    @staticmethod
    def share_created(share):
        send_mail(
            organisation_subject(_('Neue/r/s {} erstellt').format(Config.vocabulary('share'))),
            get_email_content('a_share_created', base_dict(locals())),
            get_emails_by_permission('notified_on_share_creation')
        )

    @staticmethod
    def member_created(member):
        send_mail(
            organisation_subject(_('Neue/r/s {}').format(Config.vocabulary('member_type'))),
            get_email_content('a_member_created', base_dict(locals())),
            get_emails_by_permission('notified_on_member_creation')
        )

    @staticmethod
    def member_canceled(member, end_date, message):
        send_mail(
            organisation_subject(_('{} gekündigt').format(Config.vocabulary('member_type'))),
            get_email_content('m_canceled', base_dict(locals())),
            get_emails_by_permission('notified_on_member_cancellation')
        )


class MemberNotification:
    """
    Member notification emails
    """
    @staticmethod
    def welcome(member, password):
        send_mail(
            _('Willkommen bei {0}').format(enriched_organisation('D')),
            get_email_content('welcome', base_dict(locals())),
            member.email
        )

    @staticmethod
    def welcome_co_member(co_member, password, new_shares, new=True):
        # sends either welcome mail or just information mail to new/added co-member
        send_mail(
            _('Willkommen bei {0}').format(enriched_organisation('D')),
            get_email_content('co_welcome' if new else 'co_added', base_dict(locals())),
            co_member.email
        )

    @staticmethod
    def shares_created(member, shares):
        send_mail(
            organisation_subject(_('Dein neuer Anteilschein')),
            get_email_content('s_created', base_dict(locals())),
            member.email
        )

    @staticmethod
    def email_confirmation(member):
        d = {'hash': member.get_hash()}
        send_mail(
            organisation_subject(_('E-Mail-Adresse bestätigen')),
            get_email_content('confirm', base_dict(d)),
            member.email
        )

    @staticmethod
    def reset_password(email, password):
        send_mail(
            organisation_subject(_('Dein neues Passwort')),
            get_email_content('password', base_dict(locals())),
            email
        )

    @staticmethod
    def depot_changed(emails, depot):
        send_mail(
            organisation_subject(_('{} geändert').format(Config.vocabulary('depot'))),
            get_email_content('d_changed', base_dict(locals())),
            emails
        )

    @staticmethod
    def co_member_left_subscription(primary_member, co_member, message):
        send_mail(
            organisation_subject(_('Austritt aus {}').format(Config.vocabulary('subscription'))),
            get_email_content('m_left_subscription', base_dict(locals())),
            primary_member.email
        )

    @staticmethod
    def job_signup(emails, job):
        send_mail(
            organisation_subject(_('Für Einsatz angemeldet')),
            get_email_content('j_signup', base_dict(locals())),
            emails
        )
        # ical_content = generate_ical_for_job(job)
        # Not attaching ics as it is not correct
        # msg.attach('einsatz.ics', ical_content, 'text/calendar')

    @staticmethod
    def job_reminder(emails, job, participants):
        contact = job.type.activityarea.coordinator.get_name() + ': ' + job.type.activityarea.contact()
        send_mail(
            organisation_subject(_('Einsatz-Erinnerung')),
            get_email_content('j_reminder', base_dict(locals())),
            emails
        )

    @staticmethod
    def job_time_changed(emails, job):
        send_mail(
            organisation_subject(_('Einsatz-Zeit geändert')),
            get_email_content('j_changed', base_dict(locals())),
            emails
        )
        #    ical_content = genecrate_ical_for_job(job)
        #   msg.attach('einsatz.ics', ical_content, 'text/calendar')

    @staticmethod
    def job_canceled(emails, job):
        send_mail(
            organisation_subject(_('Einsatz abgesagt')),
            get_email_content('j_canceled', base_dict(locals())),
            emails
        )
