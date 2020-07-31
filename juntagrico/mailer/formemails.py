from django.template.loader import get_template
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import EmailSender, base_dict

"""
Form emails
"""


def contact(subject, message, member, copy_to_member):
    subject = _('Anfrage per {0}:').format(Config.adminportal_name()) + subject
    email_sender = EmailSender.get_sender(subject, message)
    email_sender.send_to(Config.info_email(), reply_to=[member.email])
    if copy_to_member:
        email_sender.send_to(member.email)


def contact_member(subject, message, member, contact_member, copy_to_member, files):
    subject = _('Nachricht per {0}:').format(Config.adminportal_name()) + subject
    email_sender = EmailSender.get_sender(subject, message, reply_to=[member.email]).attach_files(files)
    email_sender.send_to(contact_member.email)
    if copy_to_member:
        email_sender.send_to(member.email)


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
    EmailSender.get_sender(subject, text_content, bcc=emails, from_email=sender)\
        .attach_html(html_content).attach_files(files).send()
