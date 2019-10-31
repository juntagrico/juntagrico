import hashlib

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.util.mailer import get_emails_by_permission, base_dict, get_email_content, filter_whitelist_emails
from juntagrico.util.organisation_name import enriched_organisation


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
        print(('Mail sent to ' + ', '.join(ok_mails) +
               (', on whitelist' if settings.DEBUG else '')))
        mailer = import_string(Config.default_mailer())
        mailer.send(msg)


'''
From forms Emails
'''


def send_contact_form(subject, message, member, copy_to_member):
    subject = _('Anfrage per {0}:').format(Config.adminportal_name()) + subject
    send_mail(subject, message, Config.info_email(), reply_to_email=member.email)
    if copy_to_member:
        send_mail(subject, message, member.email)


def send_contact_member_form(subject, message, member, contact_member, copy_to_member, attachments):
    subject = _('Nachricht per {0}:').format(Config.adminportal_name()) + subject
    send_mail(subject, message, contact_member.email, reply_to_email=member.email, attachments=attachments)
    if copy_to_member:
        send_mail(subject, message, member.email, reply_to_email=member.email, attachments=attachments)


def send_filtered_mail(subject, message, text_message, emails, attachments, sender):
    htmld = base_dict({
        'mail_template': Config.mail_template,
        'subject': subject,
        'content': message
    })
    textd = base_dict({
        'subject': subject,
        'content': text_message
    })
    text_content = get_template('mails/filtered_mail.txt').render(textd)
    html_content = get_template('mails/filtered_mail.html').render(htmld)
    send_mail(subject, text_content, emails, sender, html_message=html_content, attachments=attachments)


'''
Server generated Emails
'''


def send_new_member_in_activityarea_to_operations(area, member):
    send_mail(
        _('Neues Mitglied im Taetigkeitsbereich {0}').format(area.name),
        _('Soeben hat sich {0} {1} in den Taetigkeitsbereich {2} eingetragen').format(
            member.first_name, member.last_name, area.name
        ),
        area.get_email()
    )


def send_removed_member_in_activityarea_to_operations(area, member):
    send_mail(
        _('Mitglied verlässt Taetigkeitsbereich {0}').format(area.name),
        _('Soeben hat sich {0} {1} aus dem Taetigkeitsbereich {2} ausgetragen. '
          'Bitte lösche seine Kontaktdaten aus allen deinen Privaten Adressbüchern').format(
            member.first_name, member.last_name, area.name
        ),
        area.get_email()
    )


def send_welcome_mail(username, password, onetime_code, subscription):
    send_mail(
        _('Willkommen bei {0}').format(enriched_organisation('D')),
        get_email_content('welcome', base_dict(locals())),
        username
    )


def send_share_created_mail(member, share):
    send_mail(
        _('Dein neuer Anteilschein'),
        get_email_content('s_created', base_dict(locals())),
        member.email
    )


def send_subscription_created_mail(subscription):
    send_mail(
        _('Neuer {0} erstellt').format(Config.vocabulary('subscription')),
        get_email_content('n_sub', base_dict(locals())),
        get_emails_by_permission('new_subscription')
    )


def send_been_added_to_subscription(username, password, onetime_code, name, shares, welcome=True):
    send_mail(
        _('Willkommen bei {0}').format(enriched_organisation('D')),
        get_email_content('co_welcome' if welcome else 'co_added', base_dict(locals())),
        username
    )


def send_mail_password_reset(email, password):
    send_mail(
        _('Dein neues {0} Passwort').format(Config.organisation_name()),
        get_email_content('password', base_dict(locals())),
        email
    )


def send_job_reminder(emails, job, participants):
    contact = job.type.activityarea.coordinator.get_name() + ': ' + job.type.activityarea.contact()
    send_mail(
        _('{0} - Einsatz-Erinnerung').format(Config.organisation_name()),
        get_email_content('j_reminder', base_dict(locals())),
        emails
    )


def send_job_canceled(emails, job):
    send_mail(
        _('{0} - Einsatz abgesagt').format(Config.organisation_name()),
        get_email_content('j_canceled', base_dict(locals())),
        emails
    )


def send_confirm_mail(member):
    d = {'hash': hashlib.sha1((member.email + str(member.id)).encode('utf8')).hexdigest()}
    send_mail(
        _('{0} - Email Adresse ändern').format(Config.organisation_name()),
        get_email_content('confirm', base_dict(d)),
        member.email
    )


def send_job_time_changed(emails, job):
    send_mail(
        _('{0} - Einsatz-Zeit geändert').format(Config.organisation_name()),
        get_email_content('j_changed', base_dict(locals())),
        emails
    )
    #    ical_content = genecrate_ical_for_job(job)
    #   msg.attach('einsatz.ics', ical_content, 'text/calendar')


def send_job_signup(emails, job):
    send_mail(
        _('{0} - für Einsatz angemeldet').format(Config.organisation_name()),
        get_email_content('j_signup', base_dict(locals())),
        emails
    )
    # ical_content = generate_ical_for_job(job)
    # Not attaching ics as it is not correct
    # msg.attach('einsatz.ics', ical_content, 'text/calendar')


def send_depot_changed(emails, depot):
    send_mail(
        _('{0} - {1} geändert').format(Config.organisation_name(), Config.vocabulary('depot')),
        get_email_content('d_changed', base_dict(locals())),
        emails
    )


def send_subscription_canceled(subscription, message):
    send_mail(
        _('{0} - {1} gekündigt').format(Config.organisation_name(), Config.vocabulary('subscription')),
        get_email_content('s_canceled', base_dict(locals())),
        Config.info_email()
    )


def send_membership_canceled(member, end_date, message):
    send_mail(
        _('{0} - {1} gekündigt').format(Config.organisation_name(), Config.vocabulary('member_type')),
        get_email_content('m_canceled', base_dict(locals())),
        Config.info_email()
    )


def send_bill_share(bill, share, member):
    send_mail(
        _('{0} - Rechnung {1}').format(Config.organisation_name(), Config.vocabulary('share')),
        get_email_content('b_share', base_dict(locals())),
        member.email
    )


def send_bill_sub(bill, sub, start, end, member):
    send_mail(
        _('{0} - Rechnung {1}').format(Config.organisation_name(), Config.vocabulary('subscription')),
        get_email_content('b_sub', base_dict(locals())),
        member.email
    )


def send_bill_extrasub(bill, extrasub, start, end, member):
    send_mail(
        _('{0} - Rechnung Extra-Abo').format(Config.organisation_name()),
        get_email_content('b_esub', base_dict(locals())),
        member.email
    )
