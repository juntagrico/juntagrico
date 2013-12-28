# -*- coding: utf-8 -*-

from django.conf import settings
from django.core import mail
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives


# sends mail only to specified email-addresses if dev mode
def send_mail(subject, message, from_email, to_emails):
    print settings.DEBUG
    if settings.DEBUG is False:
        mail.send_mail(subject, message, from_email, to_emails, fail_silently=False)
    else:
        for email in to_emails:
            if email in settings.WHITELIST_EMAILS:
                mail.send_mail(subject, message, from_email, to_emails, fail_silently=False)
            else:
                print "Mail not sent to " + ", ".join(to_emails) + ", not in whitelist"
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
    msg.send()


def send_been_added_to_abo(name, email):
    send_mail('Du wurdest als Mitabonnent hinzugefuegt', "Soeben hat dich " + name + " zu seinem Abo hinzugefuegt.", 'orto@xiala.net', [email])
