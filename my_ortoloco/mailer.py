# -*- coding: utf-8 -*-

from django.conf import settings
from django.core import mail
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives
import re


# sends mail only to specified email-addresses if dev mode
def send_mail(subject, message, from_email, to_emails):
    okmails = []
    if settings.DEBUG is False:
        okmails = to_emails
    else:
        for email in to_emails:
            sent = False
            for entry in settings.WHITELIST_EMAILS:
                if sent is False and re.match(entry, email):
                    sent = True
                    okmails.append(email)
            if not sent:
                print "Mail not sent to " + ", " + email + ", not in whitelist"

    if len(okmails) > 0:
        mail.send_mail(subject, message, from_email, [email], fail_silently=False)
        print "Mail sent to " + ", ".join(okmails) + (", on whitelist" if settings.DEBUG else "")

    return None


def send_mail_multi(email_multi_message):
    print email_multi_message.to
    okmails = []
    if settings.DEBUG is False:
        okmails = email_multi_message.to
    else:
        for email in email_multi_message.to:
            sent = False
            for entry in settings.WHITELIST_EMAILS:
                if sent is False and re.match(entry, email):
                    sent = True
                    okmails.append(email)
            if not sent:
                print "Mail not sent to " + email + ", not in whitelist"


    if len(okmails) > 0:
        email_multi_message.to = []
        email_multi_message.bcc = okmails
        email_multi_message.send()
        print "Mail sent to " + ", ".join(okmails) + (", on whitelist" if settings.DEBUG else "")
    return None


def send_new_loco_in_taetigkeitsbereich_to_bg(area, loco):
    send_mail('Neues Mitglied im Taetigkeitsbereich ' + area.name,
              'Soeben hat sich ' + loco.first_name + " " + loco.last_name + ' in den Taetigkeitsbereich ' + area.name + ' eingetragen', 'orto@xiala.net', [area.coordinator.email])


def send_contact_form(subject, message, loco, copy_to_loco):
    send_mail('Anfrage per my.ortoloco: ' + subject, message, loco.email, ['orto@xiala.net'])
    if copy_to_loco:
        send_mail('Anfrage per my.ortoloco: ' + subject, message, loco.email, loco.email)


def send_welcome_mail(email, password, server):
    plaintext = get_template('mails/welcome_mail.txt')
    htmly = get_template('mails/welcome_mail.html')

    # reset password so we can send it to him
    d = Context({
        'subject': 'Willkommen bei ortoloco',
        'username': email,
        'password': password,
        'serverurl': "http://" + server
    })

    text_content = plaintext.render(d)
    html_content = htmly.render(d)

    msg = EmailMultiAlternatives('Willkommen bei ortoloco', text_content, 'orto@xiala.net', [email])
    msg.attach_alternative(html_content, "text/html")
    send_mail_multi(msg)


def send_been_added_to_abo(email, password, anteilsscheine, hash, server):
    plaintext = get_template('mails/welcome_added_mail.txt')
    htmly = get_template('mails/welcome_added_mail.html')

    # reset password so we can send it to him
    d = Context({
        'subject': 'Willkommen bei ortoloco',
        'username': email,
        'password': password,
        'hash': hash,
        'anteilsscheine': anteilsscheine,
        'serverurl': "http://" + server
    })

    text_content = plaintext.render(d)
    html_content = htmly.render(d)

    msg = EmailMultiAlternatives('Willkommen bei ortoloco', text_content, 'orto@xiala.net', [email])
    msg.attach_alternative(html_content, "text/html")
    send_mail_multi(msg)


def send_filtered_mail(subject, message, emails, server):
    plaintext = get_template('mails/filtered_mail.txt')
    htmly = get_template('mails/filtered_mail.html')

    # reset password so we can send it to him
    d = Context({
        'subject': subject,
        'content': message,
        'serverurl': "http://" + server
    })

    text_content = plaintext.render(d)
    html_content = htmly.render(d)

    msg = EmailMultiAlternatives(subject, text_content, 'info@ortoloco.ch', emails)
    msg.attach_alternative(html_content, "text/html")
    send_mail_multi(msg)

def send_mail_password_reset(email, password):
    send_mail('Dein neues ortoloco Passwort', 'Du hast dein Passwort neu setzen lassen: ' + password, 'info@ortoloco.ch', [email])
