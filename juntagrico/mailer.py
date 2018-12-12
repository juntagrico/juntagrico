import hashlib

from django.contrib.auth.models import Permission, User
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.conf import settings
from django.template.loader import get_template
from django.utils.module_loading import import_string

# from juntagrico.util.ical import *
from juntagrico.config import Config
from juntagrico.util.organisation_name import enriched_organisation


def get_server():
    return 'http://' + Config.adminportal_server_url()


def filter_whitelist_emails(to_emails):
    okmails = [x for x in to_emails if x in settings.WHITELIST_EMAILS]
    not_send = [x for x in to_emails if x not in settings.WHITELIST_EMAILS]
    print(('Mail not sent to: ' + ', '.join(not_send) + ' not in whitelist'))
    return okmails


# sends mail only to specified email-addresses if dev mode
def send_mail(subject, message, from_email, to_emails, reply_to_email=None,  html_message=None, attachments=None):
    okmails = to_emails if settings.DEBUG is False else filter_whitelist_emails(to_emails)
    if len(okmails) > 0:
        msg = EmailMultiAlternatives(subject, message, from_email, bcc=okmails, reply_to=[reply_to_email])
        if html_message is not None:
            msg.attach_alternative(html_message, 'text/html')
        if attachments is None:
            attachments = []
        for attachment in attachments:
            msg.attach(attachment.name, attachment.read())
        print(('Mail sent to ' + ', '.join(okmails) +
               (', on whitelist' if settings.DEBUG else '')))
        mailer = import_string(Config.default_mailer())
        mailer.send(msg)


'''
From forms Emails
'''


def send_contact_form(subject, message, member, copy_to_member):
    subject = 'Anfrage per ' + Config.adminportal_name() + ': ' + subject
    send_mail(subject, message, Config.info_email(), [Config.info_email()], reply_to_email=member.email)
    if copy_to_member:
        send_mail(subject, message, Config.info_email(), [member.email])


def send_contact_member_form(subject, message, member, contact_member, copy_to_member, attachments):
    subject = 'Nachricht per ' + Config.adminportal_name() + ': ' + subject
    send_mail(subject, message, Config.info_email(), [contact_member.email], reply_to_email=member.email,
              attachments=attachments)
    if copy_to_member:
        send_mail(subject, message, Config.info_email(), [member.email], reply_to_email=member.email,
                  attachments=attachments)


def send_filtered_mail(subject, message, text_message, emails, attachments, sender):
    plaintext = get_template('mails/filtered_mail.txt')
    htmly = get_template('mails/filtered_mail.html')

    htmld = {
        'mail_template': Config.mail_template,
        'subject': subject,
        'content': message,
        'serverurl': get_server()
    }
    textd = {
        'subject': subject,
        'content': text_message,
        'serverurl': get_server()
    }

    text_content = plaintext.render(textd)
    html_content = htmly.render(htmld)

    send_mail(subject, text_content, sender, emails, html_message=html_content, attachments=attachments)


'''
Server generated Emails
'''


def get_area_email(area):
    if area.email is not None:
        return [area.email]
    else:
        return [area.coordinator.email]


def send_new_member_in_activityarea_to_operations(area, member):
    emails = get_area_email(area)
    send_mail('Neues Mitglied im Taetigkeitsbereich ' + area.name,
              'Soeben hat sich ' + member.first_name + ' ' + member.last_name +
              ' in den Taetigkeitsbereich ' + area.name + ' eingetragen',
              Config.info_email(), emails)


def send_removed_member_in_activityarea_to_operations(area, member):
    emails = get_area_email(area)
    send_mail('Mitglied verlässt Taetigkeitsbereich ' + area.name,
              'Soeben hat sich ' + member.first_name + ' ' +
              member.last_name + ' aus dem Taetigkeitsbereich '
              + area.name +
              ' ausgetragen. Bitte lösche seine Kontaktdaten aus allen deinen Privaten Adressbüchern',
              Config.info_email(), emails)


def send_welcome_mail(email, password, onetime_code, subscription):
    plaintext = get_template(Config.emails('welcome'))
    d = {
        'username': email,
        'password': password,
        'onetime_code': onetime_code,
        'subscription': subscription,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    send_mail('Willkommen bei ' + enriched_organisation('D'), content, Config.info_email(), [email])


def send_share_created_mail(member, share):
    plaintext = get_template(Config.emails('s_created'))
    d = {
        'share': share,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    send_mail('Dein neuer Anteilschein', content, Config.info_email(), [member.email])


def send_subscription_created_mail(subscription):
    plaintext = get_template(Config.emails('n_sub'))
    d = {
        'subscription': subscription,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    perm = Permission.objects.get(codename='new_subscription')
    users = User.objects.filter(
        Q(groups__permissions=perm) | Q(user_permissions=perm)).distinct()
    emails = []
    for user in users:
        emails.append(user.member.email)
    if len(emails) == 0:
        emails = [Config.info_email()]
    send_mail('Neuer Anteilschein erstellt', content, Config.info_email(), emails)


def send_been_added_to_subscription(email, password, onetime_code, name, shares, welcome=True):
    if welcome:
        plaintext = get_template(Config.emails('co_welcome'))
    else:
        plaintext = get_template(Config.emails('co_added'))
    d = {
        'username': email,
        'name': name,
        'password': password,
        'onetime_code': onetime_code,
        'shares': shares,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    send_mail('Willkommen bei ' + Config.organisation_name(), content, Config.info_email(), [email])


def send_mail_password_reset(email, password):
    plaintext = get_template(Config.emails('password'))
    subject = 'Dein neues ' + Config.organisation_name() + ' Passwort'
    d = {
        'email': email,
        'password': password,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    send_mail(subject, content, Config.info_email(), [email])


def send_job_reminder(emails, job, participants):
    plaintext = get_template(Config.emails('j_reminder'))
    coordinator = job.type.activityarea.coordinator
    contact = coordinator.first_name + ' ' + \
        coordinator.last_name + ': ' + job.type.activityarea.contact()
    d = {
        'job': job,
        'participants': participants,
        'serverurl': get_server(),
        'contact': contact
    }
    content = plaintext.render(d)
    send_mail(Config.organisation_name() + ' - Job-Erinnerung', content, Config.info_email(), emails)


def send_job_canceled(emails, job):
    plaintext = get_template(Config.emails('j_canceled'))
    d = {
        'job': job,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    send_mail(Config.organisation_name() + ' - Job-Abgesagt', content, Config.info_email(), emails)


def send_confirm_mail(member):
    plaintext = get_template(Config.emails('confirm'))
    d = {
        'hash': hashlib.sha1((member.email + str(
            member.id)).encode('utf8')).hexdigest(),
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    send_mail(Config.organisation_name() + ' - Email Adresse bestätigen', content, Config.info_email(), [member.email])


def send_job_time_changed(emails, job):
    plaintext = get_template(Config.emails('j_changed'))
    d = {
        'job': job,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    #    ical_content = genecrate_ical_for_job(job)
    send_mail(Config.organisation_name() + ' - Job-Zeit geändert', content, Config.info_email(), emails)
    #   msg.attach('einsatz.ics', ical_content, 'text/calendar')


def send_job_signup(emails, job):
    plaintext = get_template(Config.emails('j_signup'))
    d = {
        'job': job,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    # ical_content = generate_ical_for_job(job)
    send_mail(Config.organisation_name() + ' - für Job Angemeldet', content, Config.info_email(), emails)
    # Not attaching ics as it is not correct
    # msg.attach('einsatz.ics', ical_content, 'text/calendar')


def send_depot_changed(emails, depot):
    plaintext = get_template(Config.emails('d_changed'))
    d = {
        'depot': depot,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    send_mail(Config.organisation_name() + ' - Depot geändert', content, Config.info_email(), emails)


def send_subscription_canceled(subscription, message):
    plaintext = get_template(Config.emails('s_canceled'))
    d = {
        'subscription': subscription,
        'message': message,
    }
    content = plaintext.render(d)
    emails = [Config.info_email()]
    send_mail(Config.organisation_name() + ' - Abo gekündigt', content, Config.info_email(), emails)


def send_membership_canceled(member, end_date, message):
    plaintext = get_template(Config.emails('m_canceled'))
    d = {
        'member': member,
        'end_date': end_date,
        'message': message,
    }
    content = plaintext.render(d)
    emails = [Config.info_email()]
    send_mail(Config.organisation_name() + ' - Abo gekündigt', content, Config.info_email(), emails)


def send_bill_share(bill, share, member):
    plaintext = get_template(Config.emails('b_share'))
    d = {
        'member': member,
        'bill': bill,
        'share': share,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    send_mail(Config.organisation_name() + ' - Rechnung Anteilschein', content, Config.info_email(), [member.email])


def send_bill_sub(bill, subscription, start, end, member):
    plaintext = get_template(Config.emails('b_sub'))
    d = {
        'member': member,
        'bill': bill,
        'sub': subscription,
        'start': start,
        'end': end,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    send_mail(Config.organisation_name() + ' - Rechnung Abo', content, Config.info_email(), [member.email])


def send_bill_extrasub(bill, extrasub, start, end, member):
    plaintext = get_template(Config.emails('b_esub'))
    d = {
        'member': member,
        'bill': bill,
        'extrasub': extrasub,
        'start': start,
        'end': end,
        'serverurl': get_server()
    }
    content = plaintext.render(d)
    send_mail(Config.organisation_name() + ' - Rechnung ExtraAbo', content, Config.info_email(), [member.email])
